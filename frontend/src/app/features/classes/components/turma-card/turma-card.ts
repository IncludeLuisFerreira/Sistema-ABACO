import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Turma } from '../../../../core/models/turma.model';

export type TurmaStatus = 'em_andamento' | 'futura' | 'encerrada';

export function getStatusTurma(inicio: string | null, fim: string | null): TurmaStatus {
  if (!inicio) return 'em_andamento';
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const dataInicio = new Date(inicio);
  dataInicio.setHours(0, 0, 0, 0);

  if (hoje < dataInicio) return 'futura';

  if (fim) {
    const dataFim = new Date(fim);
    dataFim.setHours(23, 59, 59, 999);
    if (hoje > dataFim) return 'encerrada';
  }

  return 'em_andamento';
}

export function getProgressoTurma(inicio: string | null, fim: string | null): number {
  if (!inicio || !fim) return 0;
  const hoje = new Date().getTime();
  const dataInicio = new Date(inicio).getTime();
  const dataFim = new Date(fim).getTime();
  const total = dataFim - dataInicio;
  if (total <= 0) return 100;
  const decorrido = hoje - dataInicio;
  return Math.max(0, Math.min(100, Math.round((decorrido / total) * 100)));
}

export function formatDateLabel(iso: string | null): string {
  if (!iso) return '—';
  const [ano, mes, dia] = iso.split('-');
  return `${dia}/${mes}/${ano}`;
}

@Component({
  selector: 'app-turma-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './turma-card.html',
  styleUrls: ['./turma-card.scss'],
})
export class TurmaCardComponent {
  @Input() turma!: Turma;
  @Input() deleting = false;

  @Output() edit = new EventEmitter<Turma>();
  @Output() remove = new EventEmitter<Turma>();
  @Output() duplicate = new EventEmitter<Turma>();

  get status(): TurmaStatus {
    return getStatusTurma(this.turma.dataInicio, this.turma.dataFim);
  }

  get progresso(): number {
    return getProgressoTurma(this.turma.dataInicio, this.turma.dataFim);
  }

  get statusLabel(): string {
    const map: Record<TurmaStatus, string> = {
      em_andamento: 'Em andamento',
      futura: 'Futura',
      encerrada: 'Encerrada',
    };
    return map[this.status];
  }

  get vagasLabel(): string {
    const total = this.turma.capacidade ?? 0;
    const ocupadas = this.turma.vagasOcupadas ?? 0;
    return total > 0 ? `${ocupadas}/${total} vagas` : `${ocupadas} alunos`;
  }

  get vagasPercent(): number {
    const total = this.turma.capacidade ?? 0;
    if (!total) return 0;
    return Math.round(((this.turma.vagasOcupadas ?? 0) / total) * 100);
  }

  get inicioFormatado(): string {
    return formatDateLabel(this.turma.dataInicio);
  }

  get fimFormatado(): string {
    return formatDateLabel(this.turma.dataFim);
  }
}
