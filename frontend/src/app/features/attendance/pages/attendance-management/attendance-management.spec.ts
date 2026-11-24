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
  let presencaCreate: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    matriculas$ = new Subject<Matricula[]>();
    presencasRequests = [];
    presencaCreate = vi.fn().mockReturnValue(of([]));

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
            create: presencaCreate,
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

  it('nao salva enquanto as presencas estao carregando (lista ja montada com presente false)', () => {
    matriculas$.next([matricula]);

    expect(component.students).toEqual([{ idMatricula: 10, nomeAluno: 'Aluno A', presente: false }]);
    expect(component.loadingPresencas).toBe(true);

    component.onSave();

    expect(presencaCreate).not.toHaveBeenCalled();
  });

  it('nao salva quando o carregamento das presencas falha e avisa de forma persistente', () => {
    matriculas$.next([matricula]);
    presencasRequests[0].error(new Error('500'));

    expect(component.loadFailed).toBe(true);
    expect(component.localFeedback).toContain('Não foi possível carregar as presenças');

    component.onSave();

    expect(presencaCreate).not.toHaveBeenCalled();
  });

  it('limpa o estado de falha quando um novo carregamento da certo', () => {
    matriculas$.next([matricula]);
    presencasRequests[0].error(new Error('500'));
    expect(component.loadFailed).toBe(true);

    component.onDataAulaChange('2026-03-04');
    expect(component.loadFailed).toBe(false);

    presencasRequests[1].next([presenca2]);
    expect(component.loadFailed).toBe(false);
    expect(component.loadingPresencas).toBe(false);

    component.onSave();
    expect(presencaCreate).toHaveBeenCalled();
  });
});

describe('AttendanceManagementComponent - retry de matriculas', () => {
  let matriculasRequests: Subject<Matricula[]>[];
  let presencasRequests: Subject<Presenca[]>[];
  let notifications: { success: ReturnType<typeof vi.fn>; error: ReturnType<typeof vi.fn>; clear: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    matriculasRequests = [];
    presencasRequests = [];
    notifications = { success: vi.fn(), error: vi.fn(), clear: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [AttendanceManagementComponent],
      providers: [
        { provide: TurmaService, useValue: { list: vi.fn().mockReturnValue(of([turma, turma2])) } },
        {
          provide: MatriculaService,
          useValue: {
            list: vi.fn().mockImplementation(() => {
              const matriculas$ = new Subject<Matricula[]>();
              matriculasRequests.push(matriculas$);
              return matriculas$.asObservable();
            }),
          },
        },
        {
          provide: PresencaService,
          useValue: {
            listByTurma: vi.fn().mockImplementation(() => {
              const presencas$ = new Subject<Presenca[]>();
              presencasRequests.push(presencas$);
              return presencas$.asObservable();
            }),
            create: vi.fn(),
          },
        },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();
  });

  afterEach(() => {
    matriculasRequests.forEach((m) => m.complete());
    presencasRequests.forEach((p) => p.complete());
  });

  it('recarrega as matriculas ao trocar de turma depois de uma falha', () => {
    const component = TestBed.createComponent(AttendanceManagementComponent).componentInstance;
    component.ngOnInit();
    component.dataAula = '2026-03-02';

    matriculasRequests[0].error(new Error('500'));
    expect(notifications.error).toHaveBeenCalledWith('Erro ao carregar matrículas.');

    component.onTurmaChange({ target: { value: '1' } } as unknown as Event);

    expect(matriculasRequests.length).toBe(2);
    matriculasRequests[1].next([matricula]);

    expect(component.students).toEqual([{ idMatricula: 10, nomeAluno: 'Aluno A', presente: false }]);
  });

  it('ignora a resposta de matriculas de uma requisicao anterior', () => {
    const component = TestBed.createComponent(AttendanceManagementComponent).componentInstance;
    component.ngOnInit();
    component.dataAula = '2026-03-02';
    component.onTurmaChange({ target: { value: '1' } } as unknown as Event);

    matriculasRequests[1].next([matricula, matricula2]);
    matriculasRequests[0].next([matricula]);

    expect(component.students.map((s) => s.idMatricula)).toEqual([10]);
  });
});
