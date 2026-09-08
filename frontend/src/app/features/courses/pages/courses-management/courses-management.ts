import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Curso, CursoCreatePayload, CursoUpdatePayload } from '../../../../core/models/curso.model';
import { CursoService } from '../../../../core/services/curso.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { CourseFormComponent, CourseFormSubmit } from '../../components/course-form/course-form';
import { CourseListComponent } from '../../components/course-list/course-list';

@Component({
  selector: 'app-courses-management',
  standalone: true,
  imports: [CommonModule, CourseListComponent, CourseFormComponent],
  templateUrl: './courses-management.html',
  styleUrls: ['./courses-management.scss'],
})
export class CoursesManagementComponent implements OnInit {
  cursos: Curso[] = [];
  filteredCursos: Curso[] = [];
  pagedCursos: Curso[] = [];

  searchTerm = '';
  currentPage = 1;
  readonly pageSize = 8;

  panelOpen = false;
  formMode: 'create' | 'edit' = 'create';
  selectedCurso: Curso | null = null;

  loadingList = false;
  saving = false;
  deletingCursoId: number | null = null;
  localFeedback: string | null = null;

  constructor(
    private readonly cursoService: CursoService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadCursos();
  }

  get totalPages(): number {
    const pages = Math.ceil(this.filteredCursos.length / this.pageSize);
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
    this.selectedCurso = null;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  openEdit(curso: Curso): void {
    this.formMode = 'edit';
    this.selectedCurso = curso;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedCurso = null;
  }

  onSave(payload: CourseFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;

    if (this.formMode === 'create') {
      const createPayload: CursoCreatePayload = {
        nomeCurso: payload.nomeCurso,
      };

      this.cursoService.create(createPayload).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Curso criado com sucesso.');
          this.closePanel();
          this.loadCursos();
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao criar curso.';
          this.notifications.error(message);
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
      });
      return;
    }

    if (!this.selectedCurso) {
      this.saving = false;
      return;
    }

    const updatePayload: CursoUpdatePayload = {
      nomeCurso: payload.nomeCurso,
    };

    this.cursoService.update(this.selectedCurso.idCurso, updatePayload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Curso atualizado com sucesso.');
        this.closePanel();
        this.loadCursos();
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao atualizar curso.';
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDelete(curso: Curso): void {
    this.dialog.confirm({ message: `Excluir o curso ${curso.nomeCurso}?`, confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.deletingCursoId = curso.idCurso;
      this.localFeedback = null;

      this.cursoService.delete(curso.idCurso).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Curso excluído com sucesso.');
          this.loadCursos();
          this.deletingCursoId = null;
          this.changeDetectorRef.detectChanges();
        },
        error: (error: HttpErrorResponse) => {
          if (error.status === 409) {
            const message = 'Este curso possui turmas vinculadas e nao pode ser excluido.';
            this.localFeedback = message;
            this.notifications.error(message);
          }
          this.deletingCursoId = null;
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  private loadCursos(): void {
    this.loadingList = true;
    this.cursoService.list().subscribe({
      next: (cursos) => {
        this.cursos = cursos;
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
    this.filteredCursos = this.cursos.filter((curso) => {
      if (!this.searchTerm) {
        return true;
      }

      const nome = curso.nomeCurso.toLowerCase();
      return nome.includes(this.searchTerm);
    });

    if (this.currentPage > this.totalPages) {
      this.currentPage = this.totalPages;
    }

    const start = (this.currentPage - 1) * this.pageSize;
    this.pagedCursos = this.filteredCursos.slice(start, start + this.pageSize);
  }
}
