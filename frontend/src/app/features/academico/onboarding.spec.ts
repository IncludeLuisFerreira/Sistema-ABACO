import { Type } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { Subject, of, throwError } from 'rxjs';

import { Turma } from '../../core/models/turma.model';
import { MatriculaService } from '../../core/services/matricula.service';
import { NotificationService } from '../../core/services/notification.service';
import { TurmaService } from '../../core/services/turma.service';
import { AcademicoHome } from './pages/home/home';
import { TurmasPage } from './pages/turmas/turmas';
import { AlunosPage } from './pages/alunos/alunos';

const mensagem = 'Você ainda não está cadastrado em uma turma';
const orientacao = 'Entre em contato com a administração para ser cadastrado em uma turma.';
const turma: Turma = {
  idTurma: 1,
  idCurso: 1,
  idProfessor: 2,
  capacidade: 20,
  dataInicio: null,
  dataFim: null,
  diasAula: null,
  vagasOcupadas: 0,
  avaliacoes: null,
  curso: { idCurso: 1, nomeCurso: 'Informática' },
  professor: null,
};

describe('Onboarding do professor sem turmas — issue #23', () => {
  let respostaTurmas: Subject<Turma[]>;
  let matriculas: { listMine: ReturnType<typeof vi.fn> };
  let notifications: { error: ReturnType<typeof vi.fn> };
  let router: Router;

  beforeEach(async () => {
    respostaTurmas = new Subject<Turma[]>();
    matriculas = { listMine: vi.fn().mockReturnValue(of([])) };
    notifications = { error: vi.fn() };
    await TestBed.configureTestingModule({
      imports: [AcademicoHome, TurmasPage, AlunosPage],
      providers: [
        provideRouter([]),
        { provide: TurmaService, useValue: { listMine: () => respostaTurmas } },
        { provide: MatriculaService, useValue: matriculas },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();
    router = TestBed.inject(Router);
    vi.spyOn(router, 'navigate').mockResolvedValue(true);
    vi.useFakeTimers();
  });

  afterEach(() => {
    TestBed.resetTestingModule();
    vi.useRealTimers();
  });

  function abrir<T>(component: Type<T>) {
    const fixture = TestBed.createComponent(component);
    fixture.detectChanges();
    return fixture;
  }

  it('mostra orientação antes de redirecionar automaticamente o painel vazio', () => {
    const fixture = abrir(AcademicoHome);
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
    respostaTurmas.next([]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain(mensagem);
    expect(fixture.nativeElement.textContent).toContain(orientacao);
    expect(fixture.nativeElement.querySelector('.kpi-grid')).toBeNull();
    expect(matriculas.listMine).not.toHaveBeenCalled();
    expect(notifications.error).not.toHaveBeenCalled();
    expect(router.navigate).not.toHaveBeenCalled();
    vi.advanceTimersByTime(2999);
    expect(router.navigate).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1);
    expect(router.navigate).toHaveBeenCalledExactlyOnceWith(
      ['/academico/turmas'], { replaceUrl: true },
    );
  });

  it('cancela o redirecionamento quando o professor sai do painel', () => {
    const fixture = abrir(AcademicoHome);
    respostaTurmas.next([]);
    fixture.destroy();
    vi.advanceTimersByTime(3000);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('ignora resposta tardia quando o painel já foi destruído', () => {
    const fixture = abrir(AcademicoHome);
    fixture.destroy();
    respostaTurmas.next([]);
    vi.advanceTimersByTime(3000);
    expect(router.navigate).not.toHaveBeenCalled();
    expect(matriculas.listMine).not.toHaveBeenCalled();
  });

  it('mantém os KPIs e atalhos para professor com turmas, inclusive sem matrículas', () => {
    const fixture = abrir(AcademicoHome);
    respostaTurmas.next([turma]);
    fixture.detectChanges();
    vi.advanceTimersByTime(3000);

    expect(fixture.componentInstance.totalTurmas).toBe(1);
    expect(fixture.componentInstance.totalAlunos).toBe(0);
    expect(fixture.nativeElement.querySelector('.kpi-grid')).not.toBeNull();
    expect(fixture.nativeElement.querySelector('[href="/academico/alunos"]')).not.toBeNull();
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('mostra falha de turmas no painel sem tratá-la como onboarding', () => {
    const fixture = abrir(AcademicoHome);
    respostaTurmas.error(new Error('API indisponível'));
    fixture.detectChanges();
    vi.advanceTimersByTime(3000);

    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Erro ao carregar turmas');
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('não redireciona se a consulta de matrículas falhar', () => {
    matriculas.listMine.mockReturnValue(throwError(() => new Error('API indisponível')));
    const fixture = abrir(AcademicoHome);
    respostaTurmas.next([turma]);
    fixture.detectChanges();
    vi.advanceTimersByTime(3000);

    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Erro ao carregar alunos');
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('mantém a orientação na tela de turmas vazia, sem novo redirecionamento', () => {
    const fixture = abrir(TurmasPage);
    respostaTurmas.next([]);
    fixture.detectChanges();
    vi.advanceTimersByTime(10000);

    expect(fixture.nativeElement.textContent).toContain(mensagem);
    expect(fixture.nativeElement.textContent).toContain(orientacao);
    expect(fixture.nativeElement.querySelector('[role="alert"]')).toBeNull();
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('distingue erro real de lista vazia na tela de turmas', () => {
    const fixture = abrir(TurmasPage);
    respostaTurmas.error(new Error('API indisponível'));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Erro ao carregar turmas');
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
  });

  it('continua mostrando as turmas existentes', () => {
    const fixture = abrir(TurmasPage);
    respostaTurmas.next([turma]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Informática');
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
  });

  it('orienta o professor sem turmas na tela de alunos sem notificar erro', () => {
    const fixture = abrir(AlunosPage);
    respostaTurmas.next([]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain(mensagem);
    expect(fixture.nativeElement.textContent).toContain(orientacao);
    expect(matriculas.listMine).not.toHaveBeenCalled();
    expect(notifications.error).not.toHaveBeenCalled();
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('distingue turmas sem alunos de professor sem turmas', () => {
    const fixture = abrir(AlunosPage);
    respostaTurmas.next([turma]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Nenhum aluno matriculado');
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
    expect(notifications.error).not.toHaveBeenCalled();
  });

  it('continua notificando falha real na tela de alunos', () => {
    const fixture = abrir(AlunosPage);
    respostaTurmas.error(new Error('API indisponível'));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Erro ao carregar turmas');
    expect(fixture.nativeElement.textContent).not.toContain(mensagem);
    expect(notifications.error).toHaveBeenCalledWith('Erro ao carregar turmas.');
  });
});
