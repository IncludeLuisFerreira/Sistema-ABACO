import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { DialogService } from '../../../../core/services/dialog.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { EstoqueManagementComponent } from './estoque-management';

describe('EstoqueManagementComponent - carregamento', () => {
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
