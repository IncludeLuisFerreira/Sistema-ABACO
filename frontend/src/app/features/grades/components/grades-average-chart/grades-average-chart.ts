import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { ChartComponent } from 'ng-apexcharts';
import type { ApexChart, ApexDataLabels, ApexFill, ApexPlotOptions, ApexYAxis } from 'ng-apexcharts';

import { MediaTurma } from '../../../../core/models/nota.model';
import { NotaService } from '../../../../core/services/nota.service';

@Component({
  selector: 'app-grades-average-chart',
  standalone: true,
  imports: [CommonModule, ChartComponent],
  templateUrl: './grades-average-chart.html',
  styleUrls: ['./grades-average-chart.scss'],
})
export class GradesAverageChartComponent implements OnChanges {
  @Input() turmaId: number | null = null;
  @Input() turmaNome = '';

  loading = false;
  series: { name: string; data: number[] }[] = [];
  categories: string[] = [];
  maxMedia = 10;

  chartConfig: ApexChart = {
    type: 'bar',
    height: 300,
    toolbar: { show: false },
  };

  plotOptions: ApexPlotOptions = {
    bar: {
      columnWidth: '50%',
      borderRadius: 6,
      borderRadiusApplication: 'end',
    },
  };

  yaxis: ApexYAxis = {
    min: 0,
    max: 10,
    tickAmount: 5,
    labels: {
      formatter: (val: number) => val.toFixed(1),
    },
  };

  dataLabels: ApexDataLabels = {
    enabled: true,
    formatter: (val: number) => val.toFixed(1),
    offsetY: -6,
    style: {
      fontSize: '13px',
      fontWeight: '600',
    },
  };

  fill: ApexFill = {
    colors: ['#2563eb'],
  };

  constructor(private readonly notaService: NotaService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['turmaId'] && this.turmaId) {
      this.loadMedia();
    }
  }

  private loadMedia(): void {
    if (!this.turmaId) return;

    this.loading = true;
    this.notaService.getMediaTurma(this.turmaId).subscribe({
      next: (data: MediaTurma) => {
        this.categories = data.medias.map((m) => `Prova ${m.prova}`);
        this.series = [
          {
            name: 'Média',
            data: data.medias.map((m) => m.media ?? 0),
          },
        ];
        this.loading = false;
      },
      error: () => {
        this.series = [];
        this.categories = [];
        this.loading = false;
      },
    });
  }
}
