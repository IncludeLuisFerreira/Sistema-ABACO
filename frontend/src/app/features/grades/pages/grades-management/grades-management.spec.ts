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

const matricula: Matricula = {
  idMatricula: 10,
  idAluno: 1,
  idTurma: 1,
  dataMatricula: '2026-03-01',
  status: 0,
  aluno: { idAluno: 1, nome: 'Aluno A', telefone: null },
  turma: { idTurma: 1, capacidade: 30, curso: null },
};

const nota: Nota = {
  idNota: 1,
  idMatricula: 10,
  nota: 8,
  prova: 1,
  matricula: null,
};

describe('GradesManagementComponent - carregamento', () => {
  let component: GradesManagementComponent;
  let matriculas$: Subject<Matricula[]>;
  let notas$: Subject<Nota[]>;

  beforeEach(async () => {
    matriculas$ = new Subject<Matricula[]>();
    notas$ = new Subject<Nota[]>();

    await TestBed.configureTestingModule({
      imports: [GradesManagementComponent],
      providers: [
        { provide: TurmaService, useValue: { list: vi.fn().mockReturnValue(of([turma])) } },
        {
          provide: MatriculaService,
          useValue: { list: vi.fn().mockReturnValue(matriculas$.asObservable()) },
        },
        {
          provide: NotaService,
          useValue: {
            listByTurma: vi.fn().mockReturnValue(notas$.asObservable()),
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
    notas$.complete();
  });

  it('monta a lista de alunos quando as notas chegam antes das matrículas', () => {
    notas$.next([nota]);

    expect(component.students).toEqual([]);

    matriculas$.next([matricula]);

    expect(component.students).toEqual([{ idMatricula: 10, nomeAluno: 'Aluno A', nota: 8 }]);
  });
});
