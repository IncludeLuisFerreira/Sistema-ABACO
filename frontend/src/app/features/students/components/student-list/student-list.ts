import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { Aluno } from '../../../../core/models/aluno.model';

@Component({
  selector: 'app-student-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './student-list.html',
  styleUrls: ['./student-list.scss'],
})
export class StudentListComponent {
  @Input() alunos: Aluno[] = [];
  @Input() loading = false;
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() deletingAlunoId: number | null = null;

  @Output() readonly search = new EventEmitter<string>();
  @Output() readonly edit = new EventEmitter<Aluno>();
  @Output() readonly remove = new EventEmitter<Aluno>();
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
