import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Aluno, AlunoCreatePayload, AlunoUpdatePayload } from '../../../../core/models/aluno.model';
import { AlunoService } from '../../../../core/services/aluno.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { StudentFormComponent, StudentFormSubmit } from '../../components/student-form/student-form';
import { StudentCardComponent } from '../../components/student-card/student-card';

@Component({
  selector: 'app-students-management',
  standalone: true,
  imports: [CommonModule, StudentCardComponent, StudentFormComponent],
  templateUrl: './students-management.html',
  styleUrls: ['./students-management.scss'],
})
export class StudentsManagementComponent implements OnInit {
  alunos: Aluno[] = [];
  filteredAlunos: Aluno[] = [];

  searchTerm = '';

  panelOpen = false;
  formMode: 'create' | 'edit' = 'create';
  selectedAluno: Aluno | null = null;

  loadingList = false;
  saving = false;
  deletingAlunoId: number | null = null;
  localFeedback: string | null = null;

  constructor(
    private readonly alunoService: AlunoService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadAlunos();
  }

  onSearchInput(event: Event): void {
    this.onSearch((event.target as HTMLInputElement).value);
  }

  onSearch(term: string): void {
    this.searchTerm = term.trim().toLowerCase();
    this.applyFilters();
  }

  openCreate(): void {
    this.formMode = 'create';
    this.selectedAluno = null;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  openEdit(aluno: Aluno): void {
    this.formMode = 'edit';
    this.selectedAluno = aluno;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedAluno = null;
  }

  onSave(payload: StudentFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;

    if (this.formMode === 'create') {
      const createPayload: AlunoCreatePayload = {
        nome: payload.nome,
        telefone: payload.telefone,
        dataNascimento: payload.dataNascimento,
        rua: payload.rua,
        bairro: payload.bairro,
        numero: payload.numero,
      };

      this.alunoService.create(createPayload).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Aluno criado com sucesso.');
          this.closePanel();
          this.loadAlunos();
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao criar aluno.';
          this.notifications.error(message);
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
      });
      return;
    }

    if (!this.selectedAluno) {
      this.saving = false;
      return;
    }

    const updatePayload: AlunoUpdatePayload = {
      nome: payload.nome,
      telefone: payload.telefone,
      dataNascimento: payload.dataNascimento,
      rua: payload.rua,
      bairro: payload.bairro,
      numero: payload.numero,
    };

    this.alunoService.update(this.selectedAluno.idAluno, updatePayload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Aluno atualizado com sucesso.');
        this.closePanel();
        this.loadAlunos();
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao atualizar aluno.';
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDelete(aluno: Aluno): void {
    this.dialog.confirm({ message: `Excluir o aluno ${aluno.nome}?`, confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.deletingAlunoId = aluno.idAluno;
      this.localFeedback = null;

      this.alunoService.delete(aluno.idAluno).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Aluno excluído com sucesso.');
          this.loadAlunos();
          this.deletingAlunoId = null;
          this.changeDetectorRef.detectChanges();
        },
        error: (error: HttpErrorResponse) => {
          if (error.status === 409) {
            const message = 'Este aluno possui vinculos historicos em turmas e nao pode ser excluido.';
            this.localFeedback = message;
            this.notifications.error(message);
          }
          this.deletingAlunoId = null;
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  private loadAlunos(): void {
    this.loadingList = true;
    this.alunoService.list().subscribe({
      next: (alunos) => {
        this.alunos = alunos;
        this.applyFilters();
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

  private applyFilters(): void {
    this.filteredAlunos = this.alunos.filter((aluno) => {
      if (!this.searchTerm) {
        return true;
      }
      return aluno.nome.toLowerCase().includes(this.searchTerm);
    });
  }
}
