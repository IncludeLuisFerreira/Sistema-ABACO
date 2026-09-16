import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Matricula } from '../../../../core/models/matricula.model';
import { Turma } from '../../../../core/models/turma.model';
import { Nota, NotaBatchPayload, NotaItem } from '../../../../core/models/nota.model';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { NotaService } from '../../../../core/services/nota.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { GradesAverageChartComponent } from '../../components/grades-average-chart/grades-average-chart';
import { GradesListComponent, GradeStudentRow } from '../../components/grades-list/grades-list';

@Component({
  selector: 'app-grades-management',
  standalone: true,
  imports: [CommonModule, GradesListComponent, GradesAverageChartComponent],
  templateUrl: './grades-management.html',
  styleUrls: ['./grades-management.scss'],
})
export class GradesManagementComponent implements OnInit {
  turmas: Turma[] = [];
  matriculas: Matricula[] = [];
  selectedTurma: Turma | null = null;
  prova = 1;
  students: GradeStudentRow[] = [];
  notasExistentes: Nota[] = [];

  loadingTurmas = false;
  loadingNotas = false;
  saving = false;
  localFeedback: string | null = null;

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
    private readonly notaService: NotaService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadTurmas();
    this.loadMatriculas();
  }

  onTurmaChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const turmaId = Number(target.value);
    this.selectedTurma = this.turmas.find((t) => t.idTurma === turmaId) ?? null;
    this.students = [];
    this.notasExistentes = [];

    if (this.selectedTurma) {
      this.loadMatriculas();
      this.loadNotas();
    }
    this.changeDetectorRef.detectChanges();
  }

  onProvaChange(prova: number): void {
    this.prova = prova;
    this.localFeedback = null;

    if (this.selectedTurma) {
      this.loadNotas();
    }
    this.changeDetectorRef.detectChanges();
  }

  onNotaChange(event: { idMatricula: number; nota: number | null }): void {
    const student = this.students.find((s) => s.idMatricula === event.idMatricula);
    if (student) {
      student.nota = event.nota;
      this.changeDetectorRef.detectChanges();
    }
  }

  onSave(): void {
    if (!this.selectedTurma || this.students.length === 0) {
      return;
    }

    this.saving = true;
    this.localFeedback = null;

    const notas: NotaItem[] = this.students.map((s) => ({
      idMatricula: s.idMatricula,
      nota: s.nota,
    }));

    const payload: NotaBatchPayload = {
      idTurma: this.selectedTurma.idTurma,
      prova: this.prova,
      notas,
    };

    this.notaService.create(payload).subscribe({
      next: () => {
        this.notifications.success('Notas salvas com sucesso.');
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err: HttpErrorResponse) => {
        const message = err?.error?.detail || err?.message || 'Erro ao registrar notas.';
        this.localFeedback = message;
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private loadTurmas(): void {
    this.loadingTurmas = true;
    this.turmaService.list().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        this.loadingTurmas = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.loadingTurmas = false;
        this.notifications.error('Erro ao carregar turmas.');
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private loadMatriculas(): void {
    this.matriculaService.list().subscribe({
      next: (matriculas) => {
        this.matriculas = matriculas;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar matrículas.');
      },
    });
  }

  private loadNotas(): void {
    if (!this.selectedTurma) {
      return;
    }

    this.loadingNotas = true;
    this.notaService.listByTurma(this.selectedTurma.idTurma, this.prova).subscribe({
      next: (notas) => {
        this.notasExistentes = notas;
        this.buildStudentList();
        this.loadingNotas = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notasExistentes = [];
        this.buildStudentList();
        this.loadingNotas = false;
        this.notifications.error('Erro ao carregar notas.');
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private buildStudentList(): void {
    if (!this.selectedTurma) {
      this.students = [];
      return;
    }

    const notaMap = new Map<number, number | null>();
    for (const n of this.notasExistentes) {
      notaMap.set(n.idMatricula, n.nota);
    }

    const matriculasDaTurma = this.matriculas.filter(
      (m) => m.idTurma === this.selectedTurma!.idTurma && m.status === 0
    );

    this.students = matriculasDaTurma.map((m) => ({
      idMatricula: m.idMatricula,
      nomeAluno: m.aluno?.nome ?? 'Aluno #' + m.idMatricula,
      nota: notaMap.has(m.idMatricula) ? notaMap.get(m.idMatricula)! : null,
    }));
  }
}
