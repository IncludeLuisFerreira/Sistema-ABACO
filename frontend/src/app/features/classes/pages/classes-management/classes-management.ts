import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Curso } from '../../../../core/models/curso.model';
import { Turma, TurmaCreatePayload, TurmaUpdatePayload, Avaliacao } from '../../../../core/models/turma.model';
import { Usuario } from '../../../../core/models/usuario.model';
import { CursoService } from '../../../../core/services/curso.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { UsuarioService } from '../../../../core/services/usuario.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { ClassFormComponent, ClassFormSubmit } from '../../components/class-form/class-form';
import { TurmaGrupoComponent, TurmaGrupo } from '../../components/turma-grupo/turma-grupo';
import { getStatusTurma } from '../../components/turma-card/turma-card';

@Component({
  selector: 'app-classes-management',
  standalone: true,
  imports: [CommonModule, TurmaGrupoComponent, ClassFormComponent],
  templateUrl: './classes-management.html',
  styleUrls: ['./classes-management.scss'],
})
export class ClassesManagementComponent implements OnInit {
  turmas: Turma[] = [];
  filteredTurmas: Turma[] = [];
  grupos: TurmaGrupo[] = [];
  expandedCursos = new Set<string>();

  cursos: Curso[] = [];
  professores: Usuario[] = [];

  searchTerm = '';
  semestreSelecionado = 'atual';
  semestres: { label: string; value: string }[] = [];

  panelOpen = false;
  formMode: 'create' | 'edit' = 'create';
  selectedTurma: Turma | null = null;

  loadingList = false;
  saving = false;
  deletingTurmaId: number | null = null;
  localFeedback: string | null = null;

  constructor(
    private readonly turmaService: TurmaService,
    private readonly cursoService: CursoService,
    private readonly usuarioService: UsuarioService,
    private readonly dialog: DialogService,
    private readonly notifications: NotificationService,
    // REFACTOR: detectChanges() manual repetido ~11x; adotar OnPush/signals
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadTurmas();
    this.loadCursos();
    this.loadProfessores();
  }

  onSearchInput(event: Event): string {
    return (event.target as HTMLInputElement).value;
  }

  onSearch(term: string): void {
    this.searchTerm = term.trim().toLowerCase();
    this.applyFiltersAndPagination();
  }

  getSemestreAtual(): string {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    return hoje.getMonth() < 6 ? `${ano}.1` : `${ano}.2`;
  }

  getSemestre(dataStr: string | null): string {
    if (!dataStr) return 'sem_data';
    const mes = parseInt(dataStr.split('-')[1], 10);
    const ano = dataStr.split('-')[0];
    return mes <= 6 ? `${ano}.1` : `${ano}.2`;
  }

  onSemestreChange(value: string): void {
    this.semestreSelecionado = value;
    this.applyFiltersAndPagination();
  }

  onToggleGrupo(cursoNome: string): void {
    if (this.expandedCursos.has(cursoNome)) {
      this.expandedCursos.delete(cursoNome);
    } else {
      this.expandedCursos.add(cursoNome);
    }
    this.rebuildGrupos();
  }

  expandirTodos(): void {
    this.grupos.forEach((g) => this.expandedCursos.add(g.cursoNome));
    this.rebuildGrupos();
  }

  recolherTodos(): void {
    this.expandedCursos.clear();
    this.rebuildGrupos();
  }

  openCreate(): void {
    this.formMode = 'create';
    this.selectedTurma = null;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  openEdit(turma: Turma): void {
    this.formMode = 'edit';
    this.selectedTurma = turma;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  closePanel(): void {
    this.panelOpen = false;
    this.selectedTurma = null;
  }

  onSave(payload: ClassFormSubmit): void {
    this.saving = true;
    this.localFeedback = null;

    if (this.formMode === 'create') {
      const createPayload: TurmaCreatePayload = {
        idCurso: payload.idCurso,
        idProfessor: payload.idProfessor,
        capacidade: payload.capacidade,
        dataInicio: payload.dataInicio,
        dataFim: payload.dataFim,
        diasAula: payload.diasAula,
        avaliacoes: (payload.avaliacoes as Avaliacao[]) ?? null,
      };

      this.turmaService.create(createPayload).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Turma criada com sucesso.');
          this.closePanel();
          this.loadTurmas();
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
        error: (err) => {
          const message = err?.error?.detail || err?.message || 'Erro ao criar turma.';
          this.notifications.error(message);
          this.saving = false;
          this.changeDetectorRef.detectChanges();
        },
      });
      return;
    }

    if (!this.selectedTurma) {
      this.saving = false;
      return;
    }

    const updatePayload: TurmaUpdatePayload = {
      idCurso: payload.idCurso,
      idProfessor: payload.idProfessor,
      capacidade: payload.capacidade,
      dataInicio: payload.dataInicio,
      dataFim: payload.dataFim,
      diasAula: payload.diasAula,
      avaliacoes: (payload.avaliacoes as Avaliacao[]) ?? null,
    };

    this.turmaService.update(this.selectedTurma.idTurma, updatePayload).subscribe({
      next: () => {
        this.notifications.clear();
        this.notifications.success('Turma atualizada com sucesso.');
        this.closePanel();
        this.loadTurmas();
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        const message = err?.error?.detail || err?.message || 'Erro ao atualizar turma.';
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  onDuplicate(turma: Turma): void {
    this.formMode = 'create';
    this.selectedTurma = turma;
    this.localFeedback = null;
    this.panelOpen = true;
  }

  onDelete(turma: Turma): void {
    const displayName = turma.curso?.nomeCurso ?? `Turma #${turma.idTurma}`;
    this.dialog.confirm({ message: `Excluir a turma de ${displayName}?`, confirmLabel: 'Excluir' }).subscribe(shouldDelete => {
      if (!shouldDelete) {
        return;
      }

      this.deletingTurmaId = turma.idTurma;
      this.localFeedback = null;

      this.turmaService.delete(turma.idTurma).subscribe({
        next: () => {
          this.notifications.clear();
          this.notifications.success('Turma excluída com sucesso.');
          this.loadTurmas();
          this.deletingTurmaId = null;
          this.changeDetectorRef.detectChanges();
        },
        error: (error: HttpErrorResponse) => {
          if (error.status === 409) {
            const message = 'Esta turma possui matriculas ou pedidos vinculados e nao pode ser excluida.';
            this.localFeedback = message;
            this.notifications.error(message);
          }
          this.deletingTurmaId = null;
          this.changeDetectorRef.detectChanges();
        },
      });
    });
  }

  private loadTurmas(): void {
    this.loadingList = true;
    this.turmaService.list().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        this.buildSemestres(turmas);
        this.semestreSelecionado = this.getSemestreAtual();
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

  private buildSemestres(turmas: Turma[]): void {
    const set = new Set<string>();
    for (const t of turmas) {
      if (t.dataInicio) set.add(this.getSemestre(t.dataInicio));
    }
    const atual = this.getSemestreAtual();
    const sorted = Array.from(set).sort().reverse();
    this.semestres = [
      { label: 'Semestre atual', value: 'atual' },
      ...sorted.map((s) => ({ label: s, value: s })),
      { label: 'Todos', value: 'todos' },
    ];
  }

  private loadCursos(): void {
    this.cursoService.list().subscribe({
      next: (cursos) => {
        this.cursos = cursos;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar cursos.');
      },
    });
  }

  private loadProfessores(): void {
    this.usuarioService.list().subscribe({
      next: (usuarios) => {
        this.professores = usuarios.filter((u) => u.cargo === 2);
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar professores.');
      },
    });
  }

  private applyFiltersAndPagination(): void {
    const statusOrder: Record<string, number> = {
      em_andamento: 0,
      futura: 1,
      encerrada: 2,
    };

    const semestreAlvo = this.semestreSelecionado === 'atual'
      ? this.getSemestreAtual()
      : this.semestreSelecionado;

    this.filteredTurmas = this.turmas
      .filter((turma) => {
        if (semestreAlvo !== 'todos') {
          if (this.getSemestre(turma.dataInicio) !== semestreAlvo) return false;
        }
        if (!this.searchTerm) return true;
        const cursoNome = (turma.curso?.nomeCurso ?? '').toLowerCase();
        const profNome = (turma.professor?.nome ?? '').toLowerCase();
        return cursoNome.includes(this.searchTerm) || profNome.includes(this.searchTerm);
      })
      .sort((a, b) => {
        const statusA = getStatusTurma(a.dataInicio, a.dataFim);
        const statusB = getStatusTurma(b.dataInicio, b.dataFim);
        return (statusOrder[statusA] ?? 99) - (statusOrder[statusB] ?? 99);
      });

    this.rebuildGrupos();
  }

  private rebuildGrupos(): void {
    const map = new Map<string, Turma[]>();
    for (const turma of this.filteredTurmas) {
      const key = turma.curso?.nomeCurso ?? 'Sem curso';
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(turma);
    }

    this.grupos = Array.from(map.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([cursoNome, turmas]) => ({
        cursoNome,
        turmas,
        expandido: this.expandedCursos.has(cursoNome),
      }));
  }
}
