import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { Curso } from '../../../../core/models/curso.model';

@Component({
  selector: 'app-course-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './course-list.html',
  styleUrls: ['./course-list.scss'],
})
export class CourseListComponent {
  @Input() cursos: Curso[] = [];
  @Input() loading = false;
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() deletingCursoId: number | null = null;

  @Output() readonly search = new EventEmitter<string>();
  @Output() readonly edit = new EventEmitter<Curso>();
  @Output() readonly remove = new EventEmitter<Curso>();
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
