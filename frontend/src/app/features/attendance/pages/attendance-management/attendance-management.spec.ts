import { TestBed } from '@angular/core/testing';
import { Subject, of } from 'rxjs';

import { Matricula } from '../../../../core/models/matricula.model';
import { Presenca } from '../../../../core/models/presenca.model';
import { Turma } from '../../../../core/models/turma.model';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { PresencaService } from '../../../../core/services/presenca.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { AttendanceManagementComponent } from './attendance-management';

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

const turma2: Turma = { ...turma, idTurma: 2 };

const matricula: Matricula = {
  idMatricula: 10,
  idAluno: 1,
  idTurma: 1,
  dataMatricula: '2026-03-01',
  status: 0,
  aluno: { idAluno: 1, nome: 'Aluno A', telefone: null },
  turma: { idTurma: 1, capacidade: 30, curso: null },
};

const matricula2: Matricula = {
  ...matricula,
  idMatricula: 11,
  idTurma: 2,
  aluno: { idAluno: 2, nome: 'Aluno B', telefone: null },
};

const presenca: Presenca = {
  idPresenca: 1,
  idMatricula: 10,
  dataAula: '2026-03-02',
  presente: true,
  matricula: null,
};

const presenca2: Presenca = { ...presenca, idPresenca: 2, idMatricula: 11 };

describe('AttendanceManagementComponent - carregamento', () => {
  let component: AttendanceManagementComponent;
  let matriculas$: Subject<Matricula[]>;
  let presencasRequests: Subject<Presenca[]>[];

  beforeEach(async () => {
    matriculas$ = new Subject<Matricula[]>();
    presencasRequests = [];

    await TestBed.configureTestingModule({
      imports: [AttendanceManagementComponent],
      providers: [
        { provide: TurmaService, useValue: { list: vi.fn().mockReturnValue(of([turma, turma2])) } },
        {
          provide: MatriculaService,
          useValue: { list: vi.fn().mockReturnValue(matriculas$.asObservable()) },
        },
        {
          provide: PresencaService,
          useValue: {
            listByTurma: vi.fn().mockImplementation(() => {
              const presencas$ = new Subject<Presenca[]>();
              presencasRequests.push(presencas$);
              return presencas$.asObservable();
            }),
          },
        },
        {
          provide: NotificationService,
          useValue: { success: vi.fn(), error: vi.fn(), clear: vi.fn() },
        },
      ],
    }).compileComponents();

    component = TestBed.createComponent(AttendanceManagementComponent).componentInstance;
    component.ngOnInit();
    component.dataAula = '2026-03-02';
    component.onTurmaChange({ target: { value: '1' } } as unknown as Event);
  });

  afterEach(() => {
    matriculas$.complete();
    presencasRequests.forEach((presencas$) => presencas$.complete());
  });

  it('monta a lista de alunos quando as presenças chegam antes das matrículas', () => {
    presencasRequests[0].next([presenca]);

    expect(component.students).toEqual([]);

    matriculas$.next([matricula]);

    expect(component.students).toEqual([{ idMatricula: 10, nomeAluno: 'Aluno A', presente: true }]);
  });

  it('ignora a resposta de presenças da turma anterior', () => {
    component.onTurmaChange({ target: { value: '2' } } as unknown as Event);
    matriculas$.next([matricula, matricula2]);

    presencasRequests[0].next([presenca]);
    expect(component.presencasExistentes).toEqual([]);
    expect(component.students).toEqual([
      { idMatricula: 11, nomeAluno: 'Aluno B', presente: false },
    ]);

    presencasRequests[1].next([presenca2]);
    expect(component.students).toEqual([{ idMatricula: 11, nomeAluno: 'Aluno B', presente: true }]);
  });
});
