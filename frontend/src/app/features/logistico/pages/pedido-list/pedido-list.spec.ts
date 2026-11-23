import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { Pedido } from '../../../../core/models/pedido.model';
import { AuthService } from '../../../../core/services/auth.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { PedidoService } from '../../../../core/services/pedido.service';
import { PedidoListComponent } from './pedido-list';

const pedido: Pedido = {
  idPedido: 10,
  idUsuario: 2,
  idTurma: 1,
  dataPedido: '2026-11-09',
  status: 0,
  usuario: { idUsuario: 2, nome: 'Professor' },
  turma: { idTurma: 1, capacidade: 30, nomeCurso: 'Curso Teste' },
  itens: [],
};

function setup(approveError?: { status: number; error: { detail: string } }) {
  const messages: string[] = [];
  const pedidoService = {
    list: () => of([]),
    aprovar: () => (approveError ? throwError(() => approveError) : of({ ...pedido, status: 1 })),
  };

  TestBed.configureTestingModule({
    providers: [
      { provide: PedidoService, useValue: pedidoService },
      { provide: AuthService, useValue: { getRoleFromToken: () => 'DIRECTOR', getCargo: () => 1 } },
      { provide: DialogService, useValue: { confirm: () => of(true) } },
      {
        provide: NotificationService,
        useValue: {
          clear: () => undefined,
          success: () => undefined,
          error: (message: string) => messages.push(message),
        },
      },
      { provide: Router, useValue: { navigate: () => undefined } },
    ],
  });

  const fixture = TestBed.createComponent(PedidoListComponent);
  fixture.componentInstance.ngOnInit();
  return { component: fixture.componentInstance, messages };
}

describe('PedidoListComponent - aprovação', () => {
  it('exibe a mensagem de acesso negado retornada pela API', () => {
    const { component, messages } = setup({
      status: 403,
      error: { detail: 'Apenas o Diretor pode aprovar pedidos.' },
    });

    component.onApprove(pedido);

    expect(messages).toEqual(['Apenas o Diretor pode aprovar pedidos.']);
  });

  it('exibe mensagem genérica quando a API não retorna detalhe', () => {
    const { component, messages } = setup({ status: 500, error: { detail: '' } });

    component.onApprove(pedido);

    expect(messages).toEqual(['Erro ao aprovar pedido.']);
  });
});

describe('PedidoListComponent - lista de compras', () => {
  it('mostra apenas pedidos aprovados e ainda não comprados', () => {
    const { component } = setup();
    component.pedidos = [
      { ...pedido, idPedido: 1, status: 0 },
      { ...pedido, idPedido: 2, status: 1 },
      { ...pedido, idPedido: 3, status: 2 },
      { ...pedido, idPedido: 4, status: 3 },
      { ...pedido, idPedido: 5, status: null },
    ];

    component.setTab('lista-compras');

    expect(component.filteredPedidos.map((item) => item.idPedido)).toEqual([2]);
  });

  it('mantém todos os pedidos na aba geral', () => {
    const { component } = setup();
    component.pedidos = [
      { ...pedido, idPedido: 1, status: 0 },
      { ...pedido, idPedido: 2, status: 1 },
      { ...pedido, idPedido: 3, status: 3 },
    ];

    component.setTab('todos');

    expect(component.filteredPedidos.map((item) => item.idPedido)).toEqual([1, 2, 3]);
  });

  it('troca o filtro a partir do select', () => {
    const { component } = setup();
    const event = { target: { value: 'lista-compras' } } as unknown as Event;

    component.onTabChange(event);

    expect(component.activeTab).toBe('lista-compras');
  });
});
