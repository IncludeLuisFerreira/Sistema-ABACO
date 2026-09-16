import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-academico-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './academico-layout.html',
  styleUrls: ['./academico-layout.scss'],
})
export class AcademicoLayoutComponent {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  menuOpen = false;

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
