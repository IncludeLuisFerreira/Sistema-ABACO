import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { Turma } from '../../../../core/models/turma.model';

@Component({
  selector: 'app-class-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './class-list.html',
  styleUrls: ['./class-list.scss'],
})
export class ClassListComponent {
  @Input() turmas: Turma[] = [];
  @Input() loading = false;
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() deletingTurmaId: number | null = null;

  @Output() readonly search = new EventEmitter<string>();
  @Output() readonly edit = new EventEmitter<Turma>();
  @Output() readonly remove = new EventEmitter<Turma>();
  @Output() readonly pageChange = new EventEmitter<number>();

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
