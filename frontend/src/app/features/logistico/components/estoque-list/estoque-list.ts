import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { Estoque } from '../../../../core/models/estoque.model';

@Component({
  selector: 'app-estoque-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './estoque-list.html',
  styleUrls: ['./estoque-list.scss'],
})
export class EstoqueListComponent {
  @Input() estoque: Estoque[] = [];
  @Input() loading = false;
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() deletingEstoqueId: number | null = null;
  @Input() alertaEstoqueIds: Set<number> = new Set();

  @Output() readonly search = new EventEmitter<string>();
  @Output() readonly edit = new EventEmitter<Estoque>();
  @Output() readonly remove = new EventEmitter<Estoque>();
  @Output() readonly baixa = new EventEmitter<Estoque>();
  @Output() readonly pageChange = new EventEmitter<number>();

  isAlerta(item: Estoque): boolean {
    return this.alertaEstoqueIds.has(item.idItemEstoque);
  }

  onSearch(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.search.emit(target.value);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.pageChange.emit(this.currentPage + 1);
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.pageChange.emit(this.currentPage - 1);
    }
  }
}
