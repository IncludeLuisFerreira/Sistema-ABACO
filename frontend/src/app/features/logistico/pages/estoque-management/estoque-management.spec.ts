import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { DialogService } from '../../../../core/services/dialog.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { EstoqueManagementComponent } from './estoque-management';

describe('EstoqueManagementComponent - carregamento', () => {
  let loadAll: ReturnType<typeof vi.fn>;
  let notificationError: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    loadAll = vi.fn().mockReturnValue(throwError(() => new Error('falha de rede')));
    notificationError = vi.fn();

    await TestBed.configureTestingModule({
      imports: [EstoqueManagementComponent],
      providers: [
        {
          provide: EstoqueService,
          useValue: {
            estoque$: of([]),
            loadAll,
            getAlertas: vi.fn().mockReturnValue(of([])),
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
});
