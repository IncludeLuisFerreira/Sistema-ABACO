import { ChangeDetectorRef, Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Subject, EMPTY, catchError, forkJoin, takeUntil, timeout } from 'rxjs';
import { ChartComponent } from 'ng-apexcharts';
import type {
  ApexChart, ApexDataLabels, ApexFill, ApexLegend,
  ApexNonAxisChartSeries, ApexPlotOptions, ApexResponsive,
  ApexTitleSubtitle, ApexXAxis,
} from 'ng-apexcharts';

import { AuthService } from '../../../../core/services/auth.service';
import { DashboardService } from '../../../dashboard/services/dashboard.service';
import { NotificationService } from '../../../../core/services/notification.service';
import type { Kpis, ChartAcademico, ChartLogistica } from '../../../dashboard/models/dashboard.model';

@Component({
  selector: 'app-admin-home',
  standalone: true,
  imports: [CommonModule, RouterLink, ChartComponent],
  templateUrl: './home.html',
  styleUrls: ['./home.scss'],
})
export class AdminHome implements OnInit, OnDestroy {
  readonly auth = inject(AuthService);
  private readonly dashboardService = inject(DashboardService);
  private readonly notifications = inject(NotificationService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroy$ = new Subject<void>();

  isDirector = false;
  hoje = new Date();
  kpis: Kpis = { total_alunos_ativos: 0, total_turmas_vigentes: 0, total_pedidos_pendentes: 0, total_estoque_critico: 0 };
  loading = true;
  dashboardError = false;

  donutSeries: ApexNonAxisChartSeries = [];
  donutLabels: string[] = [];
  barSeries: ApexNonAxisChartSeries = [];
  barXaxis: ApexXAxis = { categories: [] };
  consumoSeries: ApexNonAxisChartSeries = [];
  consumoXaxis: ApexXAxis = { categories: [] };

  readonly donutChart: ApexChart = { type: 'donut', height: 320, toolbar: { show: false } };
  readonly donutDataLabels: ApexDataLabels = { enabled: true, formatter: (_: string, opts: { w: { config: { series: number[] } }; seriesIndex: number }) => String(opts.w.config.series[opts.seriesIndex]) };
  readonly donutLegend: ApexLegend = { position: 'bottom' };
  readonly donutResponsive: ApexResponsive[] = [{ breakpoint: 480, options: { chart: { width: 280 }, legend: { position: 'bottom' } } }];
  readonly barChart: ApexChart = { type: 'bar', height: 320, toolbar: { show: false } };
  readonly barDataLabels: ApexDataLabels = { enabled: false };
  readonly barPlotOptions: ApexPlotOptions = { bar: { borderRadius: 6, columnWidth: '55%' } };
  readonly fill: ApexFill = { colors: ['#0f766e'] };
  readonly barTitle: ApexTitleSubtitle = { text: 'Alunos por Curso' };

  ngOnInit(): void {
    const role = this.auth.getRoleFromToken();
    this.isDirector = role === 'DIRECTOR';
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.dashboardError = false;

    const requests: any[] = [
      this.dashboardService.getKpis().pipe(takeUntil(this.destroy$), timeout(15000)),
    ];

    if (this.isDirector) {
      requests.push(
        this.dashboardService.getChartAcademico().pipe(takeUntil(this.destroy$), timeout(15000)),
        this.dashboardService.getChartLogistica().pipe(takeUntil(this.destroy$), timeout(15000)),
      );
    }

    forkJoin(requests).subscribe({
      next: (results: any[]) => {
        this.kpis = results[0] as Kpis;

        if (this.isDirector && results.length > 1) {
          this.buildAcademicoCharts(results[1] as ChartAcademico);
          this.buildLogisticaChart(results[2] as ChartLogistica);
        }

        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar dados do dashboard.');
        this.loading = false;
        this.dashboardError = true;
        this.cdr.detectChanges();
      },
    });
  }

  private buildAcademicoCharts(data: ChartAcademico): void {
    this.donutLabels = data.alunos_por_curso.map((item: { curso: string }) => item.curso);
    this.donutSeries = data.alunos_por_curso.map((item: { quantidade: number }) => item.quantidade);
    this.barXaxis = { categories: data.alunos_por_curso.map((item: { curso: string }) => item.curso) };
    this.barSeries = [{ name: 'Alunos', data: data.alunos_por_curso.map((item: { quantidade: number }) => item.quantidade) }];
  }

  private buildLogisticaChart(data: ChartLogistica): void {
    this.consumoXaxis = { categories: data.consumo_mes_atual.map((item: { item: string }) => item.item) };
    this.consumoSeries = [{ name: 'Consumo', data: data.consumo_mes_atual.map((item: { quantidade: number }) => item.quantidade) }];
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
