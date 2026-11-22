import { SimpleChange } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { NotaService } from '../../../../core/services/nota.service';
import { GradesAverageChartComponent } from './grades-average-chart';

describe('GradesAverageChartComponent', () => {
  let getMediaTurma: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    getMediaTurma = vi.fn(() => of({ medias: [{ prova: 1, media: 8.5 }] }));
    await TestBed.configureTestingModule({
      imports: [GradesAverageChartComponent],
      providers: [{ provide: NotaService, useValue: { getMediaTurma } }],
    }).compileComponents();
  });

  it('configura o grafico com largura fluida e breakpoint 768', () => {
    const fixture = TestBed.createComponent(GradesAverageChartComponent);
    const component = fixture.componentInstance;

    expect(component.chartConfig.width).toBe('100%');
    expect(component.responsive[0].breakpoint).toBe(768);
  });

  it('atualiza categorias e series quando a turma carrega', () => {
    const fixture = TestBed.createComponent(GradesAverageChartComponent);
    const component = fixture.componentInstance;

    component.turmaId = 1;
    component.ngOnChanges({ turmaId: new SimpleChange(null, 1, true) });

    expect(getMediaTurma).toHaveBeenCalledWith(1);
    expect(component.xaxis.categories).toEqual(['Prova 1']);
    expect(component.series).toEqual([{ name: 'Média', data: [8.5] }]);
  });
});
