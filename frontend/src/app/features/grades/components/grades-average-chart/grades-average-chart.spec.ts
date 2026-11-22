import { TestBed } from '@angular/core/testing';

import { NotaService } from '../../../../core/services/nota.service';
import { GradesAverageChartComponent } from './grades-average-chart';

describe('GradesAverageChartComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GradesAverageChartComponent],
      providers: [{ provide: NotaService, useValue: { getMediaTurma: vi.fn() } }],
    }).compileComponents();
  });

  it('configura o grafico com largura fluida e breakpoint 768', () => {
    const fixture = TestBed.createComponent(GradesAverageChartComponent);
    const component = fixture.componentInstance;

    expect(component.chartConfig.width).toBe('100%');
    expect(component.responsive[0].breakpoint).toBe(768);
  });
});
