import { CommonModule } from '@angular/common';
import { Component, HostListener, Input, inject } from '@angular/core';
import { Router } from '@angular/router';

import { Notificacao } from '../../../core/models/notificacao.model';
import { NotificacaoService } from '../../../core/services/notificacao.service';

@Component({
  selector: 'app-notificacao-sino',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notificacao-sino.html',
  styleUrls: ['./notificacao-sino.scss'],
})
export class NotificacaoSinoComponent {
  @Input() variant: 'sidebar' | 'topbar' = 'topbar';

  readonly service = inject(NotificacaoService);
  private readonly router = inject(Router);

  aberto = false;

  toggle(): void {
    if (this.aberto) {
      this.aberto = false;
      return;
    }
    this.aberto = true;
    this.service.carregar(0, false).subscribe();
  }

  carregarMais(): void {
    this.service.carregar(this.service.notificacoes().length, true).subscribe();
  }

  abrir(notificacao: Notificacao): void {
    if (notificacao.lida) {
      if (notificacao.link) {
        this.router.navigateByUrl(notificacao.link);
      }
      return;
    }
    this.service.marcarLida(notificacao.idNotificacao).subscribe((atualizada) => {
      if (atualizada && notificacao.link) {
        this.router.navigateByUrl(notificacao.link);
      }
    });
  }

  marcarTodas(): void {
    this.service.marcarTodas().subscribe();
  }

  fechar(): void {
    this.aberto = false;
  }

  @HostListener('document:click', ['$event'])
  aoClicarFora(event: MouseEvent): void {
    if (!this.aberto) {
      return;
    }
    const alvo = event.target as HTMLElement | null;
    if (!alvo?.closest('.notificacao-sino')) {
      this.aberto = false;
    }
  }

  @HostListener('document:keydown.escape')
  fecharComEscape(): void {
    this.aberto = false;
  }
}
