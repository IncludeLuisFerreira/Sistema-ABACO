import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { DialogService } from '../../../../core/services/dialog.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { EstoqueManagementComponent } from './estoque-management';

let loadAll: ReturnType<typeof vi.fn>;
let getAlertas: ReturnType<typeof vi.fn>;
let resetAlertasCount: ReturnType<typeof vi.fn>;
let notificationError: ReturnType<typeof vi.fn>;

beforeEach(async () => {
  loadAll = vi.fn().mockReturnValue(throwError(() => new Error('falha de rede')));
  getAlertas = vi.fn().mockReturnValue(of([]));
  resetAlertasCount = vi.fn();
  notificationError = vi.fn();

  await TestBed.configureTestingModule({
    imports: [EstoqueManagementComponent],
    providers: [
      {
        provide: EstoqueService,
        useValue: {
          estoque$: of([]),
          loadAll,
          getAlertas,
          resetAlertasCount,
        },
      },
      { provide: DialogService, useValue: { confirm: vi.fn() } },
      {
        provide: NotificationService,
        useValue: { success: vi.fn(), error: notificationError, clear: vi.fn() },
      },
    ],
  }).compileComponents();
});

describe('EstoqueManagementComponent - carregamento', () => {
  it('encerra o loading e notifica erro quando o carregamento do estoque falha', () => {
    const component = TestBed.createComponent(EstoqueManagementComponent).componentInstance;

    component.ngOnInit();

    expect(loadAll).toHaveBeenCalled();
    expect(component.loadingList).toBe(false);
    expect(notificationError).toHaveBeenCalledWith('Erro ao carregar estoque. Tente novamente.');
  });

  it('limpa os alertas e notifica erro quando o carregamento de alertas falha', () => {
    getAlertas.mockReturnValue(throwError(() => new Error('falha de rede')));
    const component = TestBed.createComponent(EstoqueManagementComponent).componentInstance;
    component.alertaEstoqueIds = new Set([1]);

    component.ngOnInit();

    expect(component.alertaEstoqueIds.size).toBe(0);
    expect(resetAlertasCount).toHaveBeenCalled();
    expect(notificationError).toHaveBeenCalledWith('Erro ao carregar alertas do estoque.');
  });
});

describe('EstoqueManagementComponent - modal de item', () => {
  function render() {
    const fixture = TestBed.createComponent(EstoqueManagementComponent);
    fixture.detectChanges();
    return fixture;
  }

  it('abre o formulário como dialog e move o foco para o primeiro campo', async () => {
    const fixture = render();
    const component = fixture.componentInstance;

    component.openCreate();
    fixture.detectChanges();
    await new Promise((resolve) => setTimeout(resolve));

    const dialog = fixture.nativeElement.querySelector('[role="dialog"]') as HTMLElement | null;
    expect(dialog).not.toBeNull();
    expect(dialog?.getAttribute('aria-modal')).toBe('true');
    expect((document.activeElement as HTMLElement | null)?.tagName).toBe('INPUT');
  });

  it('fecha com Esc quando não está salvando', () => {
    const fixture = render();
    const component = fixture.componentInstance;

    component.openCreate();
    fixture.detectChanges();
    component.onEscape();

    expect(component.panelOpen).toBe(false);
  });

  it('não fecha pelo backdrop enquanto salva', () => {
    const fixture = render();
    const component = fixture.componentInstance;

    component.openCreate();
    fixture.detectChanges();

    component.saving = true;
    component.onBackdropClick();
    expect(component.panelOpen).toBe(true);

    component.saving = false;
    component.onBackdropClick();
    expect(component.panelOpen).toBe(false);
  });

  it('devolve o foco ao elemento de origem ao fechar', async () => {
    const fixture = render();
    const component = fixture.componentInstance;
    const button = document.createElement('button');
    document.body.appendChild(button);
    button.focus();

    component.openCreate();
    fixture.detectChanges();
    component.closePanel();
    await new Promise((resolve) => setTimeout(resolve));

    expect(document.activeElement).toBe(button);
    button.remove();
  });
});
