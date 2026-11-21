import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { AuthService } from '../../../../core/services/auth.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { PedidoFormComponent } from './pedido-form';

describe('PedidoFormComponent - integridade do estoque', () => {
  let component: PedidoFormComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PedidoFormComponent],
      providers: [
        { provide: AuthService, useValue: { getRoleFromToken: () => 'DIRECTOR' } },
        { provide: EstoqueService, useValue: { search: () => of([]) } },
        { provide: TurmaService, useValue: { list: () => of([]) } },
      ],
    }).compileComponents();

    component = TestBed.createComponent(PedidoFormComponent).componentInstance;
  });

  it('exige item de estoque e quantidade maior que zero', () => {
    const item = component.itensArray.at(0);

    item.patchValue({ nomeItem: 'Papel A4', quantidade: 1 });
    expect(item.get('idItemEstoque')?.invalid).toBe(true);

    item.patchValue({ idItemEstoque: 10, quantidade: 0 });
    expect(item.get('quantidade')?.invalid).toBe(true);

    item.patchValue({ quantidade: 2 });
    expect(item.valid).toBe(true);
  });

  it('limpa o vínculo com o estoque quando o nome é editado', () => {
    const item = component.itensArray.at(0);

    component.selectItem(0, {
      idItemEstoque: 10,
      nomeItem: 'Papel A4',
      quantidadeDisponivel: 10,
      unidade: 'cx',
      estoqueMinimo: 2,
    });
    expect(item.get('idItemEstoque')?.value).toBe(10);

    component.onSearchInput(0, { target: { value: 'Papel ' } } as unknown as Event);

    expect(item.get('idItemEstoque')?.value).toBeNull();
  });
});
