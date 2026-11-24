import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  ElementRef,
  HostListener,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Aluno, AlunoCreatePayload, AlunoUpdatePayload } from '../../../../core/models/aluno.model';
import { AlunoService } from '../../../../core/services/aluno.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { StudentFormComponent, StudentFormSubmit } from '../../components/student-form/student-form';
import { StudentCardComponent } from '../../components/student-card/student-card';
import { getApiErrorMessage } from '../../../../core/utils/api-error';
import { trapFocus } from '../../../../core/utils/modal-focus';

@Component({
  selector: 'app-students-management',
  standalone: true,
  imports: [CommonModule, StudentCardComponent, StudentFormComponent],
  templateUrl: './students-management.html',
  styleUrls: ['./students-management.scss'],
})
export class StudentsManagementComponent implements OnInit, OnDestroy {
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
  formError: string | null = null;

  @ViewChild('modalCard') private modalCard?: ElementRef<HTMLElement>;
  private previouslyFocused: HTMLElement | null = null;

  constructor(
    private readonly alunoService: AlunoService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadAlunos();
  }

  ngOnDestroy(): void {
    document.body.classList.remove('abaco-modal-open');
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
    this.formError = null;
    this.openModal();
  }

  openEdit(aluno: Aluno): void {
    this.formMode = 'edit';
    this.selectedAluno = aluno;
    this.localFeedback = null;
    this.formError = null;
    this.openModal();
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedAluno = null;
    this.formError = null;
    document.body.classList.remove('abaco-modal-open');
    this.previouslyFocused?.focus();
    this.previouslyFocused = null;
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (this.panelOpen) {
      this.closePanel();
    }
  }

  onModalKeydown(event: KeyboardEvent): void {
    trapFocus(event, this.modalCard?.nativeElement);
  }

  private openModal(): void {
    if (!this.panelOpen) {
      this.previouslyFocused = document.activeElement as HTMLElement | null;
    }
    this.panelOpen = true;
    document.body.classList.add('abaco-modal-open');
    this.changeDetectorRef.detectChanges();
    this.modalCard?.nativeElement.focus();
  }

  onSave(payload: StudentFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;
    this.formError = null;

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
          this.saving = false;
          this.closePanel();
          this.loadAlunos();
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = getApiErrorMessage(err, 'Erro ao criar aluno.');
          this.formError = message;
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
        this.saving = false;
        this.closePanel();
        this.loadAlunos();
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = getApiErrorMessage(err, 'Erro ao atualizar aluno.');
        this.formError = message;
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
