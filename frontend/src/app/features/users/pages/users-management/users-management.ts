import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { CargoNivel, Usuario, UsuarioCreatePayload, UsuarioUpdatePayload } from '../../../../core/models/usuario.model';
import { NotificationService } from '../../../../core/services/notification.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { UsuarioService } from '../../../../core/services/usuario.service';
import { UsuarioFormComponent, UsuarioFormSubmit } from '../../components/usuario-form/usuario-form';
import { UsuariosListComponent } from '../../components/usuarios-list/usuarios-list';

@Component({
  selector: 'app-users-management',
  standalone: true,
  imports: [CommonModule, UsuariosListComponent, UsuarioFormComponent],
  templateUrl: './users-management.html',
  styleUrls: ['./users-management.scss'],
})
export class UsersManagementComponent implements OnInit {
  usuarios: Usuario[] = [];
  filteredUsuarios: Usuario[] = [];
  pagedUsuarios: Usuario[] = [];

  searchTerm = '';
  currentPage = 1;
  readonly pageSize = 8;

  panelOpen = false;
  formMode: 'create' | 'edit' = 'create';
  selectedUsuario: Usuario | null = null;

  loadingList = false;
  saving = false;
  deletingUserId: number | null = null;
  localFeedback: string | null = null;

  constructor(
    private readonly usuarioService: UsuarioService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadUsuarios();
  }

  get totalPages(): number {
    const pages = Math.ceil(this.filteredUsuarios.length / this.pageSize);
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
    this.selectedUsuario = null;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  openEdit(usuario: Usuario): void {
    this.formMode = 'edit';
    this.selectedUsuario = usuario;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedUsuario = null;
  }

  onSave(payload: UsuarioFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;

    if (this.formMode === 'create') {
      const createPayload: UsuarioCreatePayload = {
        nome: payload.nome,
        telefone: payload.telefone,
        email: payload.email,
        senha: payload.senha ?? '',
        cargo: payload.cargo,
      };

      this.usuarioService.create(createPayload).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Usuário criado com sucesso.');
          this.closePanel();
          this.loadUsuarios();
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao criar usuario.';
          this.notifications.error(message);
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
      });
      return;
    }

    if (!this.selectedUsuario) {
      this.saving = false;
      return;
    }

    const updatePayload: UsuarioUpdatePayload = {
      nome: payload.nome,
      telefone: payload.telefone,
      cargo: this.normalizeCargo(payload.cargo),
    };

    this.usuarioService.update(this.selectedUsuario.idUsuario, updatePayload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Usuário atualizado com sucesso.');
        this.closePanel();
        this.loadUsuarios();
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao atualizar usuario.';
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDelete(usuario: Usuario): void {
    this.dialog.confirm({ message: `Excluir o usuário ${usuario.nome || usuario.email}?`, confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.deletingUserId = usuario.idUsuario;
      this.localFeedback = null;

      this.usuarioService.delete(usuario.idUsuario).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Usuário excluído com sucesso.');
          this.loadUsuarios();
          this.deletingUserId = null;
          this.changeDetectorRef.detectChanges();
        },
        error: (error: HttpErrorResponse) => {
          if (error.status === 409) {
            const message = 'Este usuario possui vinculos historicos em turmas ou pedidos e nao pode ser excluido.';
            this.localFeedback = message;
            this.notifications.error(message);
          }
          this.deletingUserId = null;
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  private loadUsuarios(): void {
    this.loadingList = true;
    this.usuarioService.list().subscribe({
      next: (usuarios) => {
        this.usuarios = usuarios;
        this.applyFiltersAndPagination();
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

  private applyFiltersAndPagination(): void {
    this.filteredUsuarios = this.usuarios.filter((usuario) => {
      if (!this.searchTerm) {
        return true;
      }

      const nome = (usuario.nome ?? '').toLowerCase();
      const email = usuario.email.toLowerCase();
      return nome.includes(this.searchTerm) || email.includes(this.searchTerm);
    });

    if (this.currentPage > this.totalPages) {
      this.currentPage = this.totalPages;
    }

    const start = (this.currentPage - 1) * this.pageSize;
    this.pagedUsuarios = this.filteredUsuarios.slice(start, start + this.pageSize);
  }

  private normalizeCargo(cargo: number | string): CargoNivel {
    const num = Number(cargo);
    if (num === 1 || num === 2 || num === 3) {
      return num as CargoNivel;
    }

    return 3;
  }
}
