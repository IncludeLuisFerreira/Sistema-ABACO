import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TurmaService } from '../../../../core/services/turma.service';
import { Turma } from '../../../../core/models/turma.model';

@Component({
  selector: 'app-turmas',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './turmas.html',
  styleUrls: ['./turmas.scss'],
})
export class TurmasPage implements OnInit {
  turmas: Turma[] = [];
  loading = true;
  error: string | null = null;

  constructor(private readonly turmaService: TurmaService) {}

  ngOnInit(): void {
    this.turmaService.listMine().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao carregar turmas';
        this.loading = false;
      },
    });
  }

  // REFACTOR: getStatus/getProgresso reimplementam helpers de turma-card
  getStatus(turma: Turma): string {
    if (!turma.dataInicio) return 'em_andamento';
    const hoje = new Date(); hoje.setHours(0, 0, 0, 0);
    const inicio = new Date(turma.dataInicio); inicio.setHours(0, 0, 0, 0);
    if (hoje < inicio) return 'futura';
    if (turma.dataFim) {
      const fim = new Date(turma.dataFim); fim.setHours(23, 59, 59, 999);
      if (hoje > fim) return 'encerrada';
    }
    return 'em_andamento';
  }

  getProgresso(turma: Turma): number {
    if (!turma.dataInicio || !turma.dataFim) return 0;
    const hoje = new Date().getTime();
    const ini = new Date(turma.dataInicio).getTime();
    const fim = new Date(turma.dataFim).getTime();
    const total = fim - ini;
    if (total <= 0) return 100;
    return Math.max(0, Math.min(100, Math.round(((hoje - ini) / total) * 100)));
  }

  statusLabel(turma: Turma): string {
    const s = this.getStatus(turma);
    if (s === 'em_andamento') return 'Em andamento';
    if (s === 'futura') return 'Futura';
    return 'Encerrada';
  }

  formatDate(iso: string | null): string {
    if (!iso) return '—';
    const [a, m, d] = iso.split('-');
    return `${d}/${m}/${a}`;
  }
}
