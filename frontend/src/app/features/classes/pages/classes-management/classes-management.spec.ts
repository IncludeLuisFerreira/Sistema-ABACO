import { HttpErrorResponse } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { Turma } from '../../../../core/models/turma.model';
import { CursoService } from '../../../../core/services/curso.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { UsuarioService } from '../../../../core/services/usuario.service';
import { ClassFormSubmit } from '../../components/class-form/class-form';
import { ClassesManagementComponent } from './classes-management';

interface TurmaServiceMock {
  list: ReturnType<typeof vi.fn>;
  create: ReturnType<typeof vi.fn>;
  update: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
}

describe('ClassesManagementComponent', () => {
  let fixture: ComponentFixture<ClassesManagementComponent>;
  let component: ClassesManagementComponent;
  let turmaService: TurmaServiceMock;
  let notifications: NotificationService;
  let notificationErrorSpy: ReturnType<typeof vi.spyOn>;

  const payload: ClassFormSubmit = {
    capacidade: 30,
    dataInicio: '2026-02-01',
    dataFim: '2026-06-30',
    idCurso: 1,
    idProfessor: 2,
    diasAula: '1,3',
    avaliacoes: null,
  };

  const turma: Turma = {
    idTurma: 1,
    capacidade: 20,
    dataInicio: '2026-02-01',
    dataFim: '2026-06-30',
    idCurso: 1,
    idProfessor: 2,
    diasAula: '1,3',
    vagasOcupadas: 25,
    avaliacoes: null,
    curso: { idCurso: 1, nomeCurso: 'Engenharia' },
    professor: { idUsuario: 2, nome: 'Professor Teste' },
  };

  beforeEach(async () => {
    turmaService = {
      list: vi.fn().mockReturnValue(of([])),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ClassesManagementComponent],
      providers: [
        { provide: TurmaService, useValue: turmaService },
        { provide: CursoService, useValue: { list: vi.fn().mockReturnValue(of([])) } },
        { provide: UsuarioService, useValue: { list: vi.fn().mockReturnValue(of([])) } },
        { provide: DialogService, useValue: { confirm: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ClassesManagementComponent);
    component = fixture.componentInstance;
    notifications = TestBed.inject(NotificationService);
    notificationErrorSpy = vi.spyOn(notifications, 'error');
    fixture.detectChanges();
  });

  afterEach(() => {
    notifications.clear();
  });

  it('create com HTTP 422 expõe a mensagem, notifica e mantém o painel aberto', () => {
    const detail = 'Curso informado não existe';
    turmaService.create.mockReturnValue(
      throwError(() => new HttpErrorResponse({ error: { detail }, status: 422 })),
    );
    component.openCreate();

    component.onSave(payload);

    expect(turmaService.create).toHaveBeenCalledWith(
      expect.objectContaining({
        idCurso: 1,
        idProfessor: 2,
        capacidade: 30,
        dataInicio: '2026-02-01',
        dataFim: '2026-06-30',
        diasAula: '1,3',
      }),
    );
    expect(component.formError).toBe(detail);
    expect(notificationErrorSpy).toHaveBeenCalledWith(detail);
    expect(component.saving).toBe(false);
    expect(component.panelOpen).toBe(true);
  });

  it('update com HTTP 409 (capacidade abaixo das vagas) expõe a mensagem do backend', () => {
    const detail = 'Capacidade não pode ser menor que o número de vagas ocupadas (25)';
    turmaService.update.mockReturnValue(
      throwError(() => new HttpErrorResponse({ error: { detail }, status: 409 })),
    );
    component.openEdit(turma);

    component.onSave(payload);

    expect(turmaService.update).toHaveBeenCalledWith(
      1,
      expect.objectContaining({
        idCurso: 1,
        idProfessor: 2,
        capacidade: 30,
        dataInicio: '2026-02-01',
        dataFim: '2026-06-30',
        diasAula: '1,3',
      }),
    );
    expect(component.formError).toBe(detail);
    expect(notificationErrorSpy).toHaveBeenCalledWith(detail);
    expect(component.saving).toBe(false);
    expect(component.panelOpen).toBe(true);
  });
});
