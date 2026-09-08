import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TurmaService } from '../../../../core/services/turma.service';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { Turma } from '../../../../core/models/turma.model';

interface AlunoRow {
  nome: string;
  telefone: string;
  turma: string;
  idTurma: number;
  status: string;
}

@Component({
  selector: 'app-alunos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './alunos.html',
  styleUrls: ['./alunos.scss'],
})
export class AlunosPage implements OnInit {
  alunos: AlunoRow[] = [];
  todosAlunos: AlunoRow[] = [];
  turmas: Turma[] = [];
  loading = true;
  error: string | null = null;
  filtroTurma = 0;

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
    private readonly notifications: NotificationService,
  ) {}

  ngOnInit(): void { this.loadData(); }

  onFiltroChange(turmaId: number | string): void {
    const id = Number(turmaId);
    this.filtroTurma = id;
    this.alunos = id === 0
      ? this.todosAlunos
      : this.todosAlunos.filter((a) => a.idTurma === id);
  }

  private loadData(): void {
    this.turmaService.listMine().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        if (turmas.length === 0) { this.loading = false; return; }
        this.loadMatriculas(turmas);
      },
      error: () => { this.loading = false; this.error = 'Erro ao carregar turmas.'; this.notifications.error('Erro ao carregar turmas.'); },
    });
  }

  private loadMatriculas(turmas: Turma[]): void {
    this.matriculaService.listMine().subscribe({
      next: (matriculas) => {
        const turmaIds = new Set(turmas.map((t) => t.idTurma));
        const statusNomes: Record<number, string> = { 0: 'Ativa', 1: 'Concluída', 2: 'Cancelada' };

        this.todosAlunos = matriculas
          .filter((m) => turmaIds.has(m.idTurma))
          .map((m) => ({
            nome: m.aluno?.nome ?? `Aluno #${m.idAluno}`,
            telefone: m.aluno?.telefone ?? '—',
            turma: turmas.find((t) => t.idTurma === m.idTurma)?.curso?.nomeCurso ?? `Turma #${m.idTurma}`,
            idTurma: m.idTurma,
            status: statusNomes[m.status ?? 0] ?? '—',
          }));

        this.alunos = this.todosAlunos;
        this.loading = false;
      },
      error: () => { this.loading = false; this.error = 'Erro ao carregar matrículas.'; this.notifications.error('Erro ao carregar matrículas.'); },
    });
  }
}
