import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { MatriculaService } from '../../../../core/services/matricula.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { AcademicoHome } from './home';

describe('AcademicoHome', () => {
  let component: AcademicoHome;
  let fixture: ComponentFixture<AcademicoHome>;
  let turmaService: { listMine: ReturnType<typeof vi.fn> };
  let matriculaService: { listMine: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    turmaService = { listMine: vi.fn() };
    matriculaService = { listMine: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [AcademicoHome],
      providers: [
        provideRouter([]),
        { provide: TurmaService, useValue: turmaService },
        { provide: MatriculaService, useValue: matriculaService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AcademicoHome);
    component = fixture.componentInstance;
  });

  it('carrega as turmas e conta os alunos unicos', () => {
    turmaService.listMine.mockReturnValue(of([{ idTurma: 1 }]));
    matriculaService.listMine.mockReturnValue(of([{ idAluno: 1 }, { idAluno: 1 }, { idAluno: 2 }]));

    fixture.detectChanges();

    expect(component.loading).toBe(false);
    expect(component.totalTurmas).toBe(1);
    expect(component.totalAlunos).toBe(2);
    expect(component.errorMessage).toBe('');
  });

  it('exibe mensagem de erro quando /matriculas/me falha', () => {
    turmaService.listMine.mockReturnValue(of([{ idTurma: 1 }]));
    matriculaService.listMine.mockReturnValue(throwError(() => new Error('falha')));

    fixture.detectChanges();

    expect(component.loading).toBe(false);
    expect(component.totalAlunos).toBe(0);
    expect(component.errorMessage.toLowerCase()).toContain('alunos');

    const alert = fixture.nativeElement.querySelector('[role="alert"]');
    expect(alert?.textContent?.toLowerCase()).toContain('alunos');
  });

  it('exibe mensagem de erro quando /turmas/me falha e nao mostra estado vazio', () => {
    turmaService.listMine.mockReturnValue(throwError(() => new Error('falha')));

    fixture.detectChanges();

    expect(component.loading).toBe(false);
    expect(component.errorMessage.toLowerCase()).toContain('turmas');
    expect(fixture.nativeElement.querySelector('.empty-state')).toBeNull();
  });
});
