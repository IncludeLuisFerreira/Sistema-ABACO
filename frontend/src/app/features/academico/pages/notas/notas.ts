import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { TurmaService } from '../../../../core/services/turma.service';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { NotaService } from '../../../../core/services/nota.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { Turma } from '../../../../core/models/turma.model';
import { Matricula } from '../../../../core/models/matricula.model';
import { NotaItem } from '../../../../core/models/nota.model';
import { Avaliacao } from '../../../../core/models/turma.model';

interface GradeRow {
  idMatricula: number;
  nomeAluno: string;
  nota: number | null;
}

@Component({
  selector: 'app-notas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './notas.html',
  styleUrls: ['./notas.scss'],
})
export class NotasPage implements OnInit {
  turmas: Turma[] = [];
  selectedTurma: Turma | null = null;
  prova = 1;
  students: GradeRow[] = [];
  matriculas: Matricula[] = [];

  loadingTurmas = true;
  loadingNotas = false;
  saving = false;
  feedback: string | null = null;

  get provaOptions(): { value: number; label: string; peso: number }[] {
    const avs = this.selectedTurma?.avaliacoes;
    if (avs?.length) {
      return avs.map((a: Avaliacao, i: number) => ({
        value: i + 1,
        label: a.nome || `Avaliação ${i + 1}`,
        peso: a.peso || 0,
      }));
    }
    return [1, 2, 3, 4].map((n) => ({
      value: n,
      label: `${n}ª Prova`,
      peso: 10,
    }));
  }

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
    private readonly notaService: NotaService,
    private readonly notifications: NotificationService,
  ) {}

  ngOnInit(): void {
    this.loadTurmas();
  }

  onTurmaChange(turmaId: number | string): void {
    const id = Number(turmaId);
    this.selectedTurma = this.turmas.find((t) => t.idTurma === id) ?? null;
    this.students = [];
    this.feedback = null;
    if (this.selectedTurma) {
      this.loadNotas();
    }
  }

  onProvaChange(prova: number | string): void {
    this.prova = Number(prova);
    this.feedback = null;
    if (this.selectedTurma) {
      this.loadNotas();
    }
  }

  onNotaChange(idMatricula: number, value: string): void {
    const s = this.students.find((st) => st.idMatricula === idMatricula);
    if (s) {
      const num = parseFloat(value);
      s.nota = isNaN(num) ? null : num;
    }
  }

  save(): void {
    if (!this.selectedTurma || this.students.length === 0) return;

    this.saving = true;
    this.feedback = null;

    const notas: NotaItem[] = this.students.map((s) => ({
      idMatricula: s.idMatricula,
      nota: s.nota,
    }));

    this.notaService.create({ idTurma: this.selectedTurma.idTurma, prova: this.prova, notas }).subscribe({
      next: () => {
        this.notifications.success('Notas salvas com sucesso.');
        this.saving = false;
      },
      error: (err: HttpErrorResponse) => {
        this.feedback = err?.error?.detail || 'Erro ao registrar notas.';
        this.notifications.error(this.feedback!);
        this.saving = false;
      },
    });
  }

  private loadTurmas(): void {
    this.turmaService.listMine().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        this.loadingTurmas = false;
      },
      error: () => {
        this.loadingTurmas = false;
        this.notifications.error('Erro ao carregar turmas.');
      },
    });
  }

  private loadNotas(): void {
    if (!this.selectedTurma) return;

    this.loadingNotas = true;
    this.students = [];

    this.matriculaService.listMine().subscribe({
      next: (matriculas) => {
        this.matriculas = matriculas.filter(
          (m) => m.idTurma === this.selectedTurma!.idTurma && m.status === 0
        );

        if (this.matriculas.length === 0) {
          this.loadingNotas = false;
          return;
        }

        this.notaService.listByTurma(this.selectedTurma!.idTurma, this.prova).subscribe({
          next: (notas) => {
            const notaMap = new Map<number, number | null>();
            notas.forEach((n) => notaMap.set(n.idMatricula, n.nota));

            this.students = this.matriculas.map((m) => ({
              idMatricula: m.idMatricula,
              nomeAluno: m.aluno?.nome ?? `Aluno #${m.idMatricula}`,
              nota: notaMap.has(m.idMatricula) ? notaMap.get(m.idMatricula)! : null,
            }));
            this.loadingNotas = false;
          },
          error: () => {
            this.loadingNotas = false;
            this.notifications.error('Erro ao carregar notas.');
          },
        });
      },
      error: () => {
        this.loadingNotas = false;
        this.notifications.error('Erro ao carregar matrículas.');
      },
    });
  }
}
