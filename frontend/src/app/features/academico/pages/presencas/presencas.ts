import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { TurmaService } from '../../../../core/services/turma.service';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { PresencaService } from '../../../../core/services/presenca.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { Turma } from '../../../../core/models/turma.model';
import { Matricula } from '../../../../core/models/matricula.model';
import { PresencaItem } from '../../../../core/models/presenca.model';

interface StudentRow {
  idMatricula: number;
  nomeAluno: string;
  presente: boolean;
}

@Component({
  selector: 'app-presencas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './presencas.html',
  styleUrls: ['./presencas.scss'],
})
export class PresencasPage implements OnInit {
  turmas: Turma[] = [];
  selectedTurma: Turma | null = null;
  dataAula = '';
  students: StudentRow[] = [];
  matriculas: Matricula[] = [];

  loadingTurmas = true;
  loadingPresencas = false;
  saving = false;
  feedback: string | null = null;

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
    private readonly presencaService: PresencaService,
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
    if (this.selectedTurma && this.dataAula) {
      this.loadPresencas();
    }
  }

  onDataChange(data: string): void {
    this.dataAula = data;
    this.feedback = null;
    if (this.selectedTurma && this.dataAula) {
      this.loadPresencas();
    }
  }

  togglePresente(idMatricula: number): void {
    const s = this.students.find((st) => st.idMatricula === idMatricula);
    if (s) s.presente = !s.presente;
  }

  save(): void {
    if (!this.selectedTurma || !this.dataAula || this.students.length === 0) return;

    this.saving = true;
    this.feedback = null;

    const presencas: PresencaItem[] = this.students.map((s) => ({
      idMatricula: s.idMatricula,
      presente: s.presente,
    }));

    this.presencaService.create({ idTurma: this.selectedTurma.idTurma, dataAula: this.dataAula, presencas }).subscribe({
      next: () => {
        this.notifications.success('Presenças salvas com sucesso.');
        this.saving = false;
      },
      error: (err: HttpErrorResponse) => {
        this.feedback = err?.error?.detail || 'Erro ao registrar presenças.';
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

  private loadPresencas(): void {
    if (!this.selectedTurma || !this.dataAula) return;

    this.loadingPresencas = true;
    this.students = [];

    this.matriculaService.listMine().subscribe({
      next: (matriculas) => {
        this.matriculas = matriculas.filter(
          (m) => m.idTurma === this.selectedTurma!.idTurma && m.status === 0
        );

        if (this.matriculas.length === 0) {
          this.loadingPresencas = false;
          return;
        }

        this.presencaService.listByTurma(this.selectedTurma!.idTurma, this.dataAula).subscribe({
          next: (presencas) => {
            const presencaMap = new Map<number, boolean>();
            presencas.forEach((p) => {
              if (p.presente !== null) presencaMap.set(p.idMatricula, p.presente);
            });

            this.students = this.matriculas.map((m) => ({
              idMatricula: m.idMatricula,
              nomeAluno: m.aluno?.nome ?? `Aluno #${m.idMatricula}`,
              presente: presencaMap.get(m.idMatricula) ?? false,
            }));
            this.loadingPresencas = false;
          },
          error: () => {
            this.loadingPresencas = false;
            this.notifications.error('Erro ao carregar presenças.');
          },
        });
      },
      error: () => {
        this.loadingPresencas = false;
        this.notifications.error('Erro ao carregar matrículas.');
      },
    });
  }
}
