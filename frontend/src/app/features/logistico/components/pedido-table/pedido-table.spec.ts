import { TestBed } from '@angular/core/testing';

import { Pedido } from '../../../../core/models/pedido.model';
import { PedidoTableComponent } from './pedido-table';

function makePedido(status: number | null = 0): Pedido {
  return {
    idPedido: 1,
    idUsuario: 1,
    idTurma: 1,
    dataPedido: '2026-11-09',
    status,
    usuario: { idUsuario: 1, nome: 'Professor' },
    turma: { idTurma: 1, capacidade: 30, nomeCurso: 'Curso Teste' },
    itens: [],
  };
}

function setup(cargo: number | null, status: number | null = 0) {
  const fixture = TestBed.createComponent(PedidoTableComponent);
  fixture.componentInstance.pedidos = [makePedido(status)];
  fixture.componentInstance.currentUserCargo = cargo;
  fixture.detectChanges();
  return fixture;
}

function buttonLabels(fixture: ReturnType<typeof setup>): string[] {
  return Array.from<HTMLButtonElement>(fixture.nativeElement.querySelectorAll('button')).map(
    (button) => button.textContent?.trim() ?? '',
  );
}

describe('PedidoTableComponent - aprovação', () => {
  it('exibe o botão Aprovar para o Diretor em pedido solicitado', () => {
    expect(buttonLabels(setup(1, 0))).toContain('Aprovar');
  });

  it('mostra as quantidades aprovadas sem permitir edição no modo compra', () => {
    const fixture = TestBed.createComponent(PedidoTableComponent);
    fixture.componentInstance.pedidos = [
      {
        ...makePedido(1),
        itens: [
          {
            idItemPedido: 10,
            idPedido: 1,
            idItemEstoque: 2,
            nomeItem: 'Papel A4',
            quantidade: 3,
            precoUnitario: null,
            itemEstoque: { idItemEstoque: 2, nomeItem: 'Papel A4', unidade: 'cx' },
          },
        ],
      },
    ];
    fixture.componentInstance.currentUserCargo = 1;
    fixture.detectChanges();

    const comprar = Array.from<HTMLButtonElement>(fixture.nativeElement.querySelectorAll('button'))
      .find((button) => button.textContent?.trim() === 'Comprar');
    comprar?.click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.purchase-items input')).toBeNull();
    expect(fixture.nativeElement.querySelector('.purchase-item-qty')?.textContent).toContain('3');
  });

  it.each([2, 3, null])('oculta o botão Aprovar para o cargo %s', (cargo) => {
    expect(buttonLabels(setup(cargo, 0))).not.toContain('Aprovar');
  });

  it('oculta o botão Aprovar quando o pedido não está solicitado', () => {
    expect(buttonLabels(setup(1, 1))).not.toContain('Aprovar');
  });

  it('considera apenas o cargo 1 como Diretor', () => {
    const fixture = TestBed.createComponent(PedidoTableComponent);
    const component = fixture.componentInstance;

    component.currentUserCargo = 1;
    expect(component.isDirector()).toBe(true);

    for (const cargo of [2, 3, 0, null]) {
      component.currentUserCargo = cargo;
      expect(component.isDirector()).toBe(false);
    }
  });
});
