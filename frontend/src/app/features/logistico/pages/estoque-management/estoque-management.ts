import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';

import { Estoque, EstoqueCreatePayload, EstoqueUpdatePayload } from '../../../../core/models/estoque.model';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { EstoqueFormComponent, EstoqueFormSubmit } from '../../components/estoque-form/estoque-form';
import { EstoqueListComponent } from '../../components/estoque-list/estoque-list';

@Component({
  selector: 'app-estoque-management',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, EstoqueListComponent, EstoqueFormComponent],
  templateUrl: './estoque-management.html',
  styleUrls: ['./estoque-management.scss'],
})
export class EstoqueManagementComponent implements OnInit, OnDestroy {
  private readonly fb = inject(FormBuilder);
  private readonly estoqueService = inject(EstoqueService);
  private readonly dialog = inject(DialogService);
  private readonly notifications = inject(NotificationService);
  private readonly changeDetectorRef = inject(ChangeDetectorRef);

  readonly baixaForm = this.fb.nonNullable.group({
    quantidade: [0, [Validators.required, Validators.min(1)]],
    justificativa: ['', [Validators.required, Validators.minLength(1)]],
  });

  estoque: Estoque[] = [];
  filteredEstoque: Estoque[] = [];
  pagedEstoque: Estoque[] = [];
  alertaEstoqueIds: Set<number> = new Set();

  searchTerm = '';
  currentPage = 1;
  readonly pageSize = 8;

  panelOpen = false;
  formMode: 'create' | 'edit' = 'create';
  selectedItem: Estoque | null = null;

  loadingList = false;
  saving = false;
  deletingEstoqueId: number | null = null;
  localFeedback: string | null = null;

  baixaItem: Estoque | null = null;
  baixaSaving = false;

  private readonly subscriptions: Subscription[] = [];

  ngOnInit(): void {
    this.subscriptions.push(
      this.estoqueService.estoque$.subscribe((items) => {
        this.estoque = items;
        this.applyFiltersAndPagination();
        this.loadingList = false;
        this.changeDetectorRef.detectChanges();
      }),
    );
    this.loadEstoque();
    this.loadAlertas();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((s) => s.unsubscribe());
  }

  get totalPages(): number {
    const pages = Math.ceil(this.filteredEstoque.length / this.pageSize);
    return pages > 0 ? pages : 1;
  }

  onSearch(term: string): void {
    this.searchTerm = term.trim().toLowerCase();
    this.currentPage = 1;
    this.applyFiltersAndPagination();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.applyFiltersAndPagination();
  }

  openCreate(): void {
    this.formMode = 'create';
    this.selectedItem = null;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  openEdit(item: Estoque): void {
    this.formMode = 'edit';
    this.selectedItem = item;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedItem = null;
  }

  openBaixa(item: Estoque): void {
    this.baixaItem = item;
    this.baixaForm.reset({ quantidade: 0, justificativa: '' });
    this.baixaSaving = false;
  }

  closeBaixa(): void {
    this.baixaItem = null;
    this.baixaSaving = false;
  }

  submitBaixa(): void {
    if (this.baixaForm.invalid || !this.baixaItem) {
      this.baixaForm.markAllAsTouched();
      return;
    }

    this.baixaSaving = true;
    const { quantidade, justificativa } = this.baixaForm.getRawValue();

    this.estoqueService.baixa(this.baixaItem.idItemEstoque, { quantidade, justificativa }).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Baixa realizada com sucesso.');
        this.closeBaixa();
        this.loadEstoque();
        this.loadAlertas();
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao dar baixa no estoque.';
        this.notifications.error(message);
        this.baixaSaving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onSave(payload: EstoqueFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;

    if (this.formMode === 'create') {
      const createPayload: EstoqueCreatePayload = {
        nomeItem: payload.nomeItem,
        quantidadeDisponivel: payload.quantidadeDisponivel,
        unidade: payload.unidade,
        estoqueMinimo: payload.estoqueMinimo,
      };

      this.estoqueService.create(createPayload).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Item criado com sucesso.');
          this.closePanel();
          this.loadEstoque();
          this.saving = false;
          this.loadAlertas();
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao criar item.';
          this.notifications.error(message);
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
      });
      return;
    }

    if (!this.selectedItem) {
      this.saving = false;
      return;
    }

    const updatePayload: EstoqueUpdatePayload = {
      nomeItem: payload.nomeItem,
      quantidadeDisponivel: payload.quantidadeDisponivel,
      unidade: payload.unidade,
      estoqueMinimo: payload.estoqueMinimo,
    };

    this.estoqueService.update(this.selectedItem.idItemEstoque, updatePayload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Item atualizado com sucesso.');
        this.closePanel();
        this.loadEstoque();
        this.saving = false;
        this.loadAlertas();
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao atualizar item.';
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDelete(item: Estoque): void {
    this.dialog.confirm({ message: `Excluir o item ${item.nomeItem}?`, confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.deletingEstoqueId = item.idItemEstoque;
      this.localFeedback = null;

      this.estoqueService.delete(item.idItemEstoque).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Item excluído com sucesso.');
          this.deletingEstoqueId = null;
          this.loadEstoque();
          this.loadAlertas();
          this.changeDetectorRef.detectChanges();
        },
        error: (error: HttpErrorResponse) => {
          if (error.status === 409) {
            const message = 'Este item possui pedidos vinculados e nao pode ser excluido.';
            this.localFeedback = message;
            this.notifications.error(message);
          }
          this.deletingEstoqueId = null;
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  private loadEstoque(): void {
    this.loadingList = true;
    this.estoqueService.loadAll();
  }

  private loadAlertas(): void {
    this.estoqueService.getAlertas().subscribe({
      next: (alertas) => {
        this.alertaEstoqueIds = new Set(alertas.map((a) => a.idItemEstoque));
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private applyFiltersAndPagination(): void {
    this.filteredEstoque = this.estoque.filter((item) => {
      if (!this.searchTerm) {
        return true;
      }

      const nome = (item.nomeItem ?? '').toLowerCase();
      return nome.includes(this.searchTerm);
    });

    if (this.currentPage > this.totalPages) {
      this.currentPage = this.totalPages;
    }

    const start = (this.currentPage - 1) * this.pageSize;
    this.pagedEstoque = this.filteredEstoque.slice(start, start + this.pageSize);
  }
}
