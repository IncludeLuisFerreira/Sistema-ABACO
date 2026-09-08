import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { Usuario } from '../../../../core/models/usuario.model';

@Component({
  selector: 'app-usuarios-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './usuarios-list.html',
  styleUrls: ['./usuarios-list.scss'],
})
export class UsuariosListComponent {
  @Input() usuarios: Usuario[] = [];
  @Input() loading = false;
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() deletingUserId: number | null = null;

  @Output() readonly search = new EventEmitter<string>();
  @Output() readonly edit = new EventEmitter<Usuario>();
  @Output() readonly remove = new EventEmitter<Usuario>();
  @Output() readonly pageChange = new EventEmitter<number>();

  onSearch(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.search.emit(target.value);
  }

  cargoLabel(cargo: number | null): string {
    if (cargo === 1) {
      return 'Diretoria';
    }

    if (cargo === 2) {
      return 'Professor';
    }

    return 'Administrativo';
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
