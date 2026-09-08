import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';

import { Aluno } from '../../../../core/models/aluno.model';
import { Matricula, MatriculaCreatePayload, MatriculaUpdatePayload } from '../../../../core/models/matricula.model';
import { Turma } from '../../../../core/models/turma.model';
import { AlunoService } from '../../../../core/services/aluno.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { EnrollmentFormComponent, EnrollmentFormSubmit } from '../../components/enrollment-form/enrollment-form';
import { EnrollmentCardComponent } from '../../components/enrollment-card/enrollment-card';

@Component({
  selector: 'app-enrollments-management',
  standalone: true,
  imports: [CommonModule, EnrollmentCardComponent, EnrollmentFormComponent],
  templateUrl: './enrollments-management.html',
  styleUrls: ['./enrollments-management.scss'],
})
export class EnrollmentsManagementComponent implements OnInit {
  matriculas: Matricula[] = [];
  filteredMatriculas: Matricula[] = [];

  alunos: Aluno[] = [];
  turmas: Turma[] = [];

  searchTerm = '';

  panelOpen = false;
  formMode: 'create' | 'edit' = 'create';
  selectedMatricula: Matricula | null = null;

  loadingList = false;
  saving = false;
  deletingMatriculaId: number | null = null;
  localFeedback: string | null = null;

  constructor(
    private readonly router: Router,
    private readonly matriculaService: MatriculaService,
    private readonly alunoService: AlunoService,
    private readonly turmaService: TurmaService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadMatriculas();
    this.loadAlunos();
    this.loadTurmas();
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
    this.selectedMatricula = null;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  openEdit(matricula: Matricula): void {
    this.formMode = 'edit';
    this.selectedMatricula = matricula;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedMatricula = null;
  }

  onViewGrades(matriculaId: number): void {
    this.router.navigate(['/admin/matriculas', matriculaId, 'notas']);
  }

  onViewTranscript(matriculaId: number): void {
    this.router.navigate(['/admin/historico/matricula', matriculaId]);
  }

  onSave(payload: EnrollmentFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;

    if (this.formMode === 'create') {
      const createPayload: MatriculaCreatePayload = {
        idAluno: payload.idAluno,
        idTurma: payload.idTurma,
        dataMatricula: payload.dataMatricula,
        status: payload.status,
      };

      this.matriculaService.create(createPayload).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Matrícula criada com sucesso.');
          this.closePanel();
          this.loadMatriculas();
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao criar matricula.';
          this.notifications.error(message);
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
      });
      return;
    }

    if (!this.selectedMatricula) {
      this.saving = false;
      return;
    }

    const updatePayload: MatriculaUpdatePayload = {
      idAluno: payload.idAluno,
      idTurma: payload.idTurma,
      dataMatricula: payload.dataMatricula,
      status: payload.status,
    };

    this.matriculaService.update(this.selectedMatricula.idMatricula, updatePayload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Matrícula atualizada com sucesso.');
        this.closePanel();
        this.loadMatriculas();
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao atualizar matricula.';
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDelete(matricula: Matricula): void {
    const alunoNome = matricula.aluno?.nome ?? 'Matricula #' + matricula.idMatricula;
    this.dialog.confirm({ message: 'Excluir matrícula de ' + alunoNome + '?', confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.deletingMatriculaId = matricula.idMatricula;
      this.localFeedback = null;

      this.matriculaService.delete(matricula.idMatricula).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Matrícula excluída com sucesso.');
          this.loadMatriculas();
          this.deletingMatriculaId = null;
          this.changeDetectorRef.detectChanges();
        },
        error: (error: HttpErrorResponse) => {
          if (error.status === 409) {
            const message = 'Esta matricula possui vinculos e nao pode ser excluida.';
            this.localFeedback = message;
            this.notifications.error(message);
          }
          this.deletingMatriculaId = null;
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  private loadMatriculas(): void {
    this.loadingList = true;
    this.matriculaService.list().subscribe({
      next: (matriculas) => {
        this.matriculas = matriculas;
        this.applyFilters();
        this.loadingList = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        this.loadingList = false;
        this.notifications.error('Erro ao carregar matriculas. Verifique se o servidor esta rodando.');
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private loadAlunos(): void {
    this.alunoService.list().subscribe({
      next: (alunos) => {
        this.alunos = alunos;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar alunos.');
      },
    });
  }

  private loadTurmas(): void {
    this.turmaService.list().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar turmas.');
      },
    });
  }

  private applyFilters(): void {
    this.filteredMatriculas = this.matriculas.filter((m) => {
      if (!this.searchTerm) {
        return true;
      }

      const alunoNome = (m.aluno?.nome ?? '').toLowerCase();
      const turmaCurso = (m.turma?.curso?.nomeCurso ?? '').toLowerCase();
      return alunoNome.includes(this.searchTerm) || turmaCurso.includes(this.searchTerm);
    });
  }
}