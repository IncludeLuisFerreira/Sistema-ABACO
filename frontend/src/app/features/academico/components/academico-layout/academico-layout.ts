import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../../../core/services/auth.service';
import { NotificacaoService } from '../../../../core/services/notificacao.service';
import { NotificacaoSinoComponent } from '../../../../shared/components/notificacao-sino/notificacao-sino';

@Component({
  selector: 'app-academico-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, NotificacaoSinoComponent],
  templateUrl: './academico-layout.html',
  styleUrls: ['./academico-layout.scss'],
})
export class AcademicoLayoutComponent implements OnInit, OnDestroy {
  readonly auth = inject(AuthService);
  readonly notificacoes = inject(NotificacaoService);
  private readonly router = inject(Router);

  menuOpen = false;

  ngOnInit(): void {
    this.notificacoes.iniciarPolling(30000);
  }

  ngOnDestroy(): void {
    this.notificacoes.limpar();
  }

  logout(): void {
    this.notificacoes.limpar();
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
