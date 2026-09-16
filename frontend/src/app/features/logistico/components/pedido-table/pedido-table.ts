import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Pedido, ItemPedido, getPedidoStatusLabel, getPedidoStatusClass } from '../../../../core/models/pedido.model';

@Component({
  selector: 'app-pedido-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pedido-table.html',
  styleUrls: ['./pedido-table.scss'],
})
export class PedidoTableComponent {
  @Input() pedidos: Pedido[] = [];
  @Input() loading = false;
  @Input() currentUserCargo: number | null = null;

  @Output() readonly approve = new EventEmitter<Pedido>();
  @Output() readonly confirmPurchase = new EventEmitter<{ pedido: Pedido; itens: { idItemPedido: number; quantidade: number }[] }>();
  @Output() readonly deliver = new EventEmitter<Pedido>();
  @Output() readonly remove = new EventEmitter<Pedido>();

  getStatusLabel = getPedidoStatusLabel;
  getStatusClass = getPedidoStatusClass;

  purchasingPedidoId: number | null = null;
  purchaseQtys: Record<number, number> = {};

  startPurchase(pedido: Pedido): void {
    this.purchasingPedidoId = pedido.idPedido;
    this.purchaseQtys = {};
    if (pedido.itens) {
      for (const item of pedido.itens) {
        this.purchaseQtys[item.idItemPedido] = item.quantidade ?? 0;
      }
    }
  }

  onConfirmPurchase(pedido: Pedido): void {
    const itens = Object.entries(this.purchaseQtys).map(([id, qtd]) => ({
      idItemPedido: Number(id),
      quantidade: qtd,
    }));
    this.confirmPurchase.emit({ pedido, itens });
    this.purchasingPedidoId = null;
    this.purchaseQtys = {};
  }

  onCancelPurchase(): void {
    this.purchasingPedidoId = null;
    this.purchaseQtys = {};
  }

  canApprove(status: number | null): boolean {
    return status === 0;
  }

  canPurchase(status: number | null): boolean {
    return status === 1;
  }

  canDeliver(status: number | null): boolean {
    return status === 2;
  }

  isDirector(): boolean {
    return this.currentUserCargo === 1;
  }

  trackById(_index: number, item: ItemPedido): number {
    return item.idItemPedido;
  }
}
