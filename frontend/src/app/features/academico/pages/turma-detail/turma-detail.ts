import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TurmaService } from '../../../../core/services/turma.service';
import { NotaService } from '../../../../core/services/nota.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { Turma, Avaliacao } from '../../../../core/models/turma.model';
import { Nota } from '../../../../core/models/nota.model';

interface FaixaNota {
  label: string;
  min: number;
  max: number;
  count: number;
  color: string;
}

@Component({
  selector: 'app-turma-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './turma-detail.html',
  styleUrls: ['./turma-detail.scss'],
})
export class TurmaDetailPage implements OnInit {
  turma: Turma | null = null;
  notas: Nota[] = [];
  faixas: FaixaNota[] = [];
  maxFaixaCount = 0;
  mediaGeral = 0;

  loading = true;
  error: string | null = null;

  provaSelecionada = 1;

  faixaPadrao: FaixaNota[] = [
    { label: '0 – 2', min: 0, max: 1.99, count: 0, color: '#dc2626' },
    { label: '2 – 4', min: 2, max: 3.99, count: 0, color: '#f97316' },
    { label: '4 – 6', min: 4, max: 5.99, count: 0, color: '#eab308' },
    { label: '6 – 8', min: 6, max: 7.99, count: 0, color: '#22c55e' },
    { label: '8 – 10', min: 8, max: 10, count: 0, color: '#16a34a' },
  ];

  get provasDisponiveis(): { value: number; label: string }[] {
    const avs = this.turma?.avaliacoes;
    if (avs?.length) {
      return avs.map((a: Avaliacao, i: number) => ({
        value: i + 1,
        label: a.nome || `Avaliação ${i + 1}`,
      }));
    }
    return [1, 2, 3, 4].map((n) => ({
      value: n,
      label: `${n}ª Prova`,
    }));
  }

  constructor(
    private readonly route: ActivatedRoute,
    private readonly turmaService: TurmaService,
    private readonly notaService: NotaService,
    private readonly notifications: NotificationService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) {
      this.error = 'Turma não encontrada';
      this.loading = false;
      return;
    }

    this.turmaService.getById(id).subscribe({
      next: (turma) => {
        this.turma = turma;
        this.loadNotas(turma.idTurma);
      },
      error: () => {
        this.error = 'Turma não encontrada ou você não tem acesso a ela';
        this.loading = false;
      },
    });
  }

  private loadNotas(turmaId: number): void {
    this.notaService.listByTurma(turmaId, this.provaSelecionada).subscribe({
      next: (notas) => {
        this.notas = notas;
        this.calcularDistribuicao();
        this.loading = false;
      },
      error: () => {
        this.notas = [];
        this.calcularDistribuicao();
        this.loading = false;
      },
    });
  }

  onProvaChange(prova: number): void {
    this.provaSelecionada = Number(prova);
    if (!this.turma) return;
    this.notaService.listByTurma(this.turma.idTurma, this.provaSelecionada).subscribe({
      next: (notas) => {
        this.notas = notas;
        this.calcularDistribuicao();
      },
      error: () => {
        this.notifications.error('Erro ao carregar notas desta prova');
      },
    });
  }

  private calcularDistribuicao(): void {
    const notasValidas = this.notas.filter((n) => n.nota !== null && n.nota !== undefined);
    this.faixas = this.faixaPadrao.map((f) => {
      const count = notasValidas.filter(
        (n) => n.nota! >= f.min && n.nota! <= f.max
      ).length;
      return { ...f, count };
    });
    this.maxFaixaCount = Math.max(...this.faixas.map((f) => f.count), 1);
    const soma = notasValidas.reduce((acc, n) => acc + n.nota!, 0);
    this.mediaGeral = notasValidas.length > 0
      ? Math.round((soma / notasValidas.length) * 10) / 10
      : 0;
  }

  getStatus(): string {
    if (!this.turma?.dataInicio) return 'em_andamento';
    const hoje = new Date(); hoje.setHours(0, 0, 0, 0);
    const inicio = new Date(this.turma.dataInicio); inicio.setHours(0, 0, 0, 0);
    if (hoje < inicio) return 'futura';
    if (this.turma.dataFim) {
      const fim = new Date(this.turma.dataFim); fim.setHours(23, 59, 59, 999);
      if (hoje > fim) return 'encerrada';
    }
    return 'em_andamento';
  }

  statusLabel(): string {
    const s = this.getStatus();
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
