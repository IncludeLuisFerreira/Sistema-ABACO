import { TestBed } from '@angular/core/testing';
import { Subject, of } from 'rxjs';

import { Matricula } from '../../../../core/models/matricula.model';
import { Nota } from '../../../../core/models/nota.model';
import { Turma } from '../../../../core/models/turma.model';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { NotaService } from '../../../../core/services/nota.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { GradesManagementComponent } from './grades-management';

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

const nota: Nota = {
  idNota: 1,
  idMatricula: 10,
  nota: 8,
  prova: 1,
  matricula: null,
};

const nota2: Nota = { ...nota, idNota: 2, idMatricula: 11, nota: 9 };

describe('GradesManagementComponent - carregamento', () => {
  let component: GradesManagementComponent;
  let matriculas$: Subject<Matricula[]>;
  let notasRequests: Subject<Nota[]>[];

  beforeEach(async () => {
    matriculas$ = new Subject<Matricula[]>();
    notasRequests = [];

    await TestBed.configureTestingModule({
      imports: [GradesManagementComponent],
      providers: [
        { provide: TurmaService, useValue: { list: vi.fn().mockReturnValue(of([turma, turma2])) } },
        {
          provide: MatriculaService,
          useValue: { list: vi.fn().mockReturnValue(matriculas$.asObservable()) },
        },
        {
          provide: NotaService,
          useValue: {
            listByTurma: vi.fn().mockImplementation(() => {
              const notas$ = new Subject<Nota[]>();
              notasRequests.push(notas$);
              return notas$.asObservable();
            }),
            getMediaTurma: vi.fn().mockReturnValue(of({ idTurma: 1, medias: [] })),
          },
        },
        {
          provide: NotificationService,
          useValue: { success: vi.fn(), error: vi.fn(), clear: vi.fn() },
        },
      ],
    }).compileComponents();

    component = TestBed.createComponent(GradesManagementComponent).componentInstance;
    component.ngOnInit();
    component.onTurmaChange({ target: { value: '1' } } as unknown as Event);
  });

  afterEach(() => {
    matriculas$.complete();
    notasRequests.forEach((notas$) => notas$.complete());
  });

  it('monta a lista de alunos quando as notas chegam antes das matrículas', () => {
    notasRequests[0].next([nota]);

    expect(component.students).toEqual([]);

    matriculas$.next([matricula]);

    expect(component.students).toEqual([{ idMatricula: 10, nomeAluno: 'Aluno A', nota: 8 }]);
  });

  it('ignora a resposta de notas da turma anterior', () => {
    component.onTurmaChange({ target: { value: '2' } } as unknown as Event);
    matriculas$.next([matricula, matricula2]);

    notasRequests[0].next([nota]);
    expect(component.notasExistentes).toEqual([]);
    expect(component.students).toEqual([{ idMatricula: 11, nomeAluno: 'Aluno B', nota: null }]);

    notasRequests[1].next([nota2]);
    expect(component.students).toEqual([{ idMatricula: 11, nomeAluno: 'Aluno B', nota: 9 }]);
  });
});
