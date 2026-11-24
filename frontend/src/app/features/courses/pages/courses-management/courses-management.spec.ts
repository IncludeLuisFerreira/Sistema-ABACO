import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { CursoService } from '../../../../core/services/curso.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { CoursesManagementComponent } from './courses-management';

describe('CoursesManagementComponent - modal de curso', () => {
  let fixture: ReturnType<typeof TestBed.createComponent<CoursesManagementComponent>>;
  let component: CoursesManagementComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CoursesManagementComponent],
      providers: [
        {
          provide: CursoService,
          useValue: {
            list: vi.fn().mockReturnValue(of([])),
            create: vi.fn(),
            update: vi.fn(),
            delete: vi.fn(),
          },
        },
        { provide: DialogService, useValue: { confirm: vi.fn() } },
        {
          provide: NotificationService,
          useValue: { success: vi.fn(), error: vi.fn(), clear: vi.fn() },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CoursesManagementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    component.closePanel();
    document.body.classList.remove('abaco-modal-open');
  });

  function overlay(): HTMLElement | null {
    return fixture.nativeElement.querySelector('.abaco-modal-overlay');
  }

  it('abre o formulário em modal sobreposto e trava o scroll do fundo', () => {
    component.openCreate();
    fixture.detectChanges();

    const dialog = fixture.nativeElement.querySelector('[role="dialog"]') as HTMLElement;

    expect(overlay()).not.toBeNull();
    expect(dialog.getAttribute('aria-modal')).toBe('true');
    expect(document.body.classList.contains('abaco-modal-open')).toBe(true);
    expect(document.activeElement).toBe(dialog);
  });

  it('fecha o modal com ESC e libera o scroll do fundo', () => {
    component.openCreate();
    fixture.detectChanges();

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    fixture.detectChanges();

    expect(component.panelOpen).toBe(false);
    expect(overlay()).toBeNull();
    expect(document.body.classList.contains('abaco-modal-open')).toBe(false);
  });

  it('fecha ao clicar no backdrop e ignora clique dentro do card', () => {
    component.openCreate();
    fixture.detectChanges();

    const dialog = fixture.nativeElement.querySelector('.abaco-modal-card') as HTMLElement;
    dialog.click();
    fixture.detectChanges();
    expect(component.panelOpen).toBe(true);

    overlay()!.click();
    fixture.detectChanges();
    expect(component.panelOpen).toBe(false);
  });

  it('esc com modal fechado não altera o estado', () => {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));

    expect(component.panelOpen).toBe(false);
  });

  it('prende o foco no card com Tab', () => {
    component.openCreate();
    fixture.detectChanges();

    const card = fixture.nativeElement.querySelector('.abaco-modal-card') as HTMLElement;
    const focusables = Array.from(
      card.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ),
    );
    const last = focusables[focusables.length - 1];
    last.focus();

    card.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }));

    expect(document.activeElement).toBe(focusables[0]);
  });

  it('mantém o modal aberto e exibe o erro quando o save falha', () => {
    const detail = 'Já existe um curso com esse nome.';
    TestBed.inject(CursoService).create = vi
      .fn()
      .mockReturnValue(throwError(() => new HttpErrorResponse({ error: { detail }, status: 409 })));
    component.openCreate();
    fixture.detectChanges();

    component.onSave({ nomeCurso: 'Curso Teste' });
    fixture.detectChanges();

    expect(component.panelOpen).toBe(true);
    expect(component.formError).toBe(detail);
    expect(
      (fixture.nativeElement.querySelector('.error--block') as HTMLElement).textContent,
    ).toContain(detail);
  });

  it('libera o scroll do fundo ao destruir o componente com o modal aberto', () => {
    component.openCreate();
    fixture.detectChanges();

    fixture.destroy();

    expect(document.body.classList.contains('abaco-modal-open')).toBe(false);
  });
});
