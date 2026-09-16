import { CommonModule } from '@angular/common';
import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';

import { Matricula } from '../../../../core/models/matricula.model';

@Component({
  selector: 'app-enrollment-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './enrollment-list.html',
  styleUrls: ['./enrollment-list.scss'],
})
export class EnrollmentListComponent {
  @Input() matriculas: Matricula[] = [];
  @Input() loading = false;
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() deletingMatriculaId: number | null = null;

  @Output() readonly search = new EventEmitter<string>();
  @Output() readonly edit = new EventEmitter<Matricula>();
  @Output() readonly remove = new EventEmitter<Matricula>();
  @Output() readonly viewGrades = new EventEmitter<number>();
  @Output() readonly viewTranscript = new EventEmitter<number>();
  @Output() readonly pageChange = new EventEmitter<number>();

  openDropdownId: number | null = null;

  toggleDropdown(matriculaId: number): void {
    this.openDropdownId = this.openDropdownId === matriculaId ? null : matriculaId;
  }

  closeDropdown(): void {
    this.openDropdownId = null;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown')) {
      this.openDropdownId = null;
    }
  }

  statusLabel(status: number | null): string {
    if (status === 0) return 'Ativa';
    if (status === 1) return 'Concluida';
    if (status === 2) return 'Cancelada';
    return '---';
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
