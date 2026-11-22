import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { Subject, of, throwError } from 'rxjs';

import { Turma } from '../../../../core/models/turma.model';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { NotaService } from '../../../../core/services/nota.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { NotasPage } from './notas';

const turma: Turma = {
  idTurma: 1,
  capacidade: 30,
  dataInicio: '2026-03-01',
  dataFim: '2026-06-30',
  idCurso: 1,
  idProfessor: 2,
  diasAula: '1,3',
  vagasOcupadas: 1,
  avaliacoes: null,
  curso: { idCurso: 1, nomeCurso: 'Curso Teste' },
  professor: { idUsuario: 2, nome: 'Professor Teste' },
};

describe('NotasPage - validação', () => {
  let component: NotasPage;
  let notaCreate: ReturnType<typeof vi.fn>;
  let notifications: { success: ReturnType<typeof vi.fn>; error: ReturnType<typeof vi.fn> };
  let turmas$: Subject<Turma[]>;

  beforeEach(async () => {
    turmas$ = new Subject<Turma[]>();
    notaCreate = vi.fn().mockReturnValue(of([]));
    notifications = { success: vi.fn(), error: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [NotasPage],
      providers: [
        { provide: TurmaService, useValue: { listMine: vi.fn().mockReturnValue(turmas$.asObservable()) } },
        { provide: MatriculaService, useValue: { listMine: vi.fn().mockReturnValue(of([])) } },
        {
          provide: NotaService,
          useValue: { listByTurma: vi.fn().mockReturnValue(of([])), create: notaCreate },
        },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(NotasPage);
    component = fixture.componentInstance;
    turmas$.next([turma]);
    turmas$.complete();
    fixture.detectChanges();
  });

  it('bloqueia envio de nota fora de 0–10', () => {
    component.selectedTurma = turma;
    component.students = [{ idMatricula: 10, nomeAluno: 'Aluno A', nota: 11 }];

    component.save();

    expect(notaCreate).not.toHaveBeenCalled();
    expect(component.feedback).toBe('As notas devem estar entre 0 e 10.');
    expect(notifications.error).toHaveBeenCalledWith('As notas devem estar entre 0 e 10.');
  });

  it('traduz o erro 422 do backend', () => {
    const error = new HttpErrorResponse({
      status: 422,
      error: { detail: [{ loc: ['body', 'notas', 0, 'nota'], msg: 'Input should be less than or equal to 10' }] },
    });
    notaCreate.mockReturnValueOnce(throwError(() => error));

    component.selectedTurma = turma;
    component.students = [{ idMatricula: 10, nomeAluno: 'Aluno A', nota: 8 }];

    component.save();

    expect(component.feedback).toBe('O valor deve ser menor ou igual a 10.');
    expect(notifications.error).toHaveBeenCalledWith('O valor deve ser menor ou igual a 10.');
  });
});
