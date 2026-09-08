import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../../../core/services/auth.service';
import { EstoqueService } from '../../../../core/services/estoque.service';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './admin-layout.html',
  styleUrls: ['./admin-layout.scss'],
})
export class AdminLayoutComponent implements OnInit, OnDestroy {
  readonly auth = inject(AuthService);
  readonly estoqueService = inject(EstoqueService);
  private readonly router = inject(Router);

  private pollInterval: ReturnType<typeof setInterval> | null = null;

  menuOpen = false;

  ngOnInit(): void {
    this.estoqueService.loadAlertasCount();
    this.pollInterval = setInterval(() => {
      this.estoqueService.loadAlertasCount();
    }, 30000);
  }

  ngOnDestroy(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  logout(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
