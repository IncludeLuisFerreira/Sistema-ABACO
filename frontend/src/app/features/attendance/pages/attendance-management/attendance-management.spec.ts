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

const matricula: Matricula = {
  idMatricula: 10,
  idAluno: 1,
  idTurma: 1,
  dataMatricula: '2026-03-01',
  status: 0,
  aluno: { idAluno: 1, nome: 'Aluno A', telefone: null },
  turma: { idTurma: 1, capacidade: 30, curso: null },
};

const presenca: Presenca = {
  idPresenca: 1,
  idMatricula: 10,
  dataAula: '2026-03-02',
  presente: true,
  matricula: null,
};

describe('AttendanceManagementComponent - carregamento', () => {
  let component: AttendanceManagementComponent;
  let matriculas$: Subject<Matricula[]>;
  let presencas$: Subject<Presenca[]>;

  beforeEach(async () => {
    matriculas$ = new Subject<Matricula[]>();
    presencas$ = new Subject<Presenca[]>();

    await TestBed.configureTestingModule({
      imports: [AttendanceManagementComponent],
      providers: [
        { provide: TurmaService, useValue: { list: vi.fn().mockReturnValue(of([turma])) } },
        {
          provide: MatriculaService,
          useValue: { list: vi.fn().mockReturnValue(matriculas$.asObservable()) },
        },
        {
          provide: PresencaService,
          useValue: { listByTurma: vi.fn().mockReturnValue(presencas$.asObservable()) },
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
    presencas$.complete();
  });

  it('monta a lista de alunos quando as presenças chegam antes das matrículas', () => {
    presencas$.next([presenca]);

    expect(component.students).toEqual([]);

    matriculas$.next([matricula]);

    expect(component.students).toEqual([{ idMatricula: 10, nomeAluno: 'Aluno A', presente: true }]);
  });
});
