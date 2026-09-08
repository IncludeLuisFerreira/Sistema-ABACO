import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService, decodePayload, getStoredToken } from '../../../../core/services/auth.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { Pedido, PedidoCompraPayload, getPedidoStatusLabel, getPedidoStatusClass } from '../../../../core/models/pedido.model';
import { PedidoService } from '../../../../core/services/pedido.service';
import { PedidoTableComponent } from '../../components/pedido-table/pedido-table';

@Component({
  selector: 'app-pedido-list',
  standalone: true,
  imports: [CommonModule, PedidoTableComponent],
  templateUrl: './pedido-list.html',
  styleUrls: ['./pedido-list.scss'],
})
export class PedidoListComponent implements OnInit {
  pedidos: Pedido[] = [];
  activeTab: 'todos' | 'lista-compras' = 'todos';

  loadingList = false;
  currentUserCargo: number | null = null;

  constructor(
    private readonly pedidoService: PedidoService,
    private readonly authService: AuthService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    const token = getStoredToken();
    if (token) {
      const payload = decodePayload(token);
      this.currentUserCargo = payload.cargo ?? null;
    }
    this.loadPedidos();
  }

  get approvedPedidos(): Pedido[] {
    return this.pedidos.filter((p) => p.status !== null && p.status! >= 1);
  }

  get filteredPedidos(): Pedido[] {
    if (this.activeTab === 'lista-compras') {
      return this.approvedPedidos;
    }
    return this.pedidos;
  }

  setTab(tab: 'todos' | 'lista-compras'): void {
    this.activeTab = tab;
  }

  onApprove(pedido: Pedido): void {
    this.dialog.confirm({ message: `Aprovar o pedido #${pedido.idPedido}?`, confirmLabel: 'Aprovar' }).subscribe(shouldApprove => {
      if (!shouldApprove) {
        return;
      }

      this.pedidoService.aprovar(pedido.idPedido).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Pedido aprovado com sucesso.');
          this.loadPedidos();
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao aprovar pedido.';
          this.notifications.error(message);
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  onConfirmPurchase(event: { pedido: Pedido; itens: { idItemPedido: number; quantidade: number }[] }): void {
    const payload: PedidoCompraPayload = { itens: event.itens };
    this.pedidoService.comprar(event.pedido.idPedido, payload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Compra confirmada com sucesso.');
        this.loadPedidos();
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao marcar pedido como comprado.';
        this.notifications.error(message);
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDeliver(pedido: Pedido): void {
    this.dialog.confirm({ message: `Entregar pedido #${pedido.idPedido}? Os itens serão adicionados ao estoque.`, confirmLabel: 'Entregar' }).subscribe(shouldDeliver => {
      if (!shouldDeliver) {
        return;
      }

      this.pedidoService.entregar(pedido.idPedido).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Pedido entregue com sucesso.');
          this.loadPedidos();
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao entregar pedido.';
          this.notifications.error(message);
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  onDelete(pedido: Pedido): void {
    this.dialog.confirm({ message: `Excluir o pedido #${pedido.idPedido}?`, confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.pedidoService.delete(pedido.idPedido).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Pedido excluído com sucesso.');
          this.loadPedidos();
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao excluir pedido.';
          this.notifications.error(message);
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  newPedido(): void {
    const role = this.authService.getRoleFromToken();
    const route = role === 'TEACHER' ? '/academico/pedidos/novo' : '/admin/logistico/pedidos/novo';
    this.router.navigate([route]);
  }

  private loadPedidos(): void {
    this.loadingList = true;
    this.pedidoService.list().subscribe({
      next: (pedidos) => {
        this.pedidos = pedidos;
        this.loadingList = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.loadingList = false;
        this.notifications.error('Erro ao carregar. Tente novamente.');
        this.changeDetectorRef.detectChanges();
      },
    });
  }
}
