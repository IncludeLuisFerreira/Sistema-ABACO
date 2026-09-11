import { ChangeDetectorRef, Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Subject, EMPTY, catchError, takeUntil, timeout } from 'rxjs';
import { ChartComponent } from 'ng-apexcharts';
import type {
  ApexChart,
  ApexDataLabels,
  ApexFill,
  ApexLegend,
  ApexNonAxisChartSeries,
  ApexPlotOptions,
  ApexResponsive,
  ApexTitleSubtitle,
  ApexXAxis,
} from 'ng-apexcharts';

import { DashboardService } from '../../services/dashboard.service';
import { NotificationService } from '../../../../core/services/notification.service';
import type { Kpis, ChartAcademico, ChartLogistica } from '../../models/dashboard.model';

@Component({
  selector: 'app-dashboard-home',
  standalone: true,
  imports: [CommonModule, RouterLink, ChartComponent],
  templateUrl: './home.html',
  styleUrls: ['./home.scss'],
})
// REFACTOR: app-dashboard-home não é referenciado por rota (dead code)
export class Home implements OnInit, OnDestroy {
  private readonly dashboardService = inject(DashboardService);
  private readonly notifications = inject(NotificationService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroy$ = new Subject<void>();

  kpis: Kpis = {
    total_alunos_ativos: 0,
    total_turmas_vigentes: 0,
    total_pedidos_pendentes: 0,
    total_estoque_critico: 0,
  };

  loading = true;

  donutSeries: ApexNonAxisChartSeries = [];
  donutLabels: string[] = [];
  donutChart: ApexChart = {
    type: 'donut',
    height: 320,
    toolbar: { show: false },
  };
  donutTitle: ApexTitleSubtitle = {
    text: 'Alunos por Curso',
    align: 'left',
    style: { fontSize: '16px', fontWeight: '600' },
  };
  donutLegend: ApexLegend = { position: 'bottom' };
  donutResponsive: ApexResponsive[] = [
    { breakpoint: 480, options: { chart: { height: 260 }, legend: { position: 'bottom' } } },
  ];
  donutDataLabels: ApexDataLabels = { enabled: false };
  donutFill: ApexFill = {
    colors: ['#2563eb', '#7c3aed', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#ec4899', '#8b5cf6'],
  };

  barSeries: { name: string; data: number[] }[] = [];
  barCategories: string[] = [];
  barChart: ApexChart = {
    type: 'bar',
    height: 320,
    toolbar: { show: false },
  };
  barTitle: ApexTitleSubtitle = {
    text: 'Status das Matrículas',
    align: 'left',
    style: { fontSize: '16px', fontWeight: '600' },
  };
  barPlotOptions: ApexPlotOptions = {
    bar: { columnWidth: '50%', borderRadius: 6, borderRadiusApplication: 'end' },
  };
  barDataLabels: ApexDataLabels = { enabled: true, offsetY: -6, style: { fontSize: '13px', fontWeight: '600' } };
  barXaxis: ApexXAxis = { categories: [] };
  barFill: ApexFill = { colors: ['#2563eb'] };

  consumoSeries: { name: string; data: number[] }[] = [];
  consumoCategories: string[] = [];
  consumoChart: ApexChart = {
    type: 'bar',
    height: 320,
    toolbar: { show: false },
  };
  consumoTooltip = {
    enabled: true,
    y: { formatter: (val: number) => `${val} unidades` },
  };
  consumoTitle: ApexTitleSubtitle = {
    text: 'Consumo de Estoque (Mês Atual)',
    align: 'left',
    style: { fontSize: '16px', fontWeight: '600' },
  };
  consumoPlotOptions: ApexPlotOptions = {
    bar: { columnWidth: '50%', borderRadius: 6, borderRadiusApplication: 'end', horizontal: true },
  };
  consumoDataLabels: ApexDataLabels = { enabled: true, style: { fontSize: '13px', fontWeight: '600' } };
  consumoXaxis: ApexXAxis = { categories: [] };
  consumoFill: ApexFill = { colors: ['#f59e0b'] };

  private readonly statusLabels: Record<number, string> = {
    0: 'Ativas',
    1: 'Concluídas',
    2: 'Canceladas',
  };

  private pendingCount = 0;

  ngOnInit(): void {
    this.loadAll();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadAll(): void {
    this.loading = true;
    this.pendingCount = 3;

    this.dashboardService
      .getKpis()
      .pipe(
        takeUntil(this.destroy$),
        timeout(15000),
        catchError(() => {
          this.notifications.error('Erro ao carregar indicadores.');
          this.decrementPending();
          return EMPTY;
        }),
      )
      .subscribe((data) => {
        this.kpis = data;
        this.decrementPending();
      });

    this.dashboardService
      .getChartAcademico()
      .pipe(
        takeUntil(this.destroy$),
        timeout(15000),
        catchError(() => {
          this.notifications.error('Erro ao carregar gráficos acadêmicos.');
          this.decrementPending();
          return EMPTY;
        }),
      )
      .subscribe((data) => {
        this.buildDonut(data);
        this.buildBar(data);
        this.decrementPending();
      });

    this.dashboardService
      .getChartLogistica()
      .pipe(
        takeUntil(this.destroy$),
        timeout(15000),
        catchError(() => {
          this.notifications.error('Erro ao carregar gráficos de logística.');
          this.decrementPending();
          return EMPTY;
        }),
      )
      .subscribe((data) => {
        this.buildConsumo(data);
        this.decrementPending();
      });
  }

  private decrementPending(): void {
    this.pendingCount--;
    if (this.pendingCount <= 0) {
      this.loading = false;
      this.cdr.detectChanges();
    }
  }

  private buildDonut(data: ChartAcademico): void {
    this.donutLabels = data.alunos_por_curso.map((c) => c.curso);
    this.donutSeries = data.alunos_por_curso.map((c) => c.quantidade);
  }

  private buildBar(data: ChartAcademico): void {
    const labels: string[] = [];
    const values: number[] = [];

    for (const item of data.status_matriculas) {
      labels.push(this.statusLabels[item.status] ?? `Status ${item.status}`);
      values.push(item.quantidade);
    }

    this.barCategories = labels;
    this.barXaxis = { categories: labels };
    this.barSeries = [{ name: 'Matrículas', data: values }];
  }

  private buildConsumo(data: ChartLogistica): void {
    this.consumoCategories = data.consumo_mes_atual.map((c) => c.item);
    this.consumoXaxis = { categories: data.consumo_mes_atual.map((c) => c.item) };
    this.consumoSeries = [{ name: 'Consumo', data: data.consumo_mes_atual.map((c) => c.quantidade) }];
  }
}
