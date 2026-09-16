import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService, mapCargoToRole } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-access-denied',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './access-denied.html',
  styleUrls: ['./access-denied.scss'],
})
export class AccessDenied implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  roleName = '';

  ngOnInit(): void {
    const role = this.auth.getRoleFromToken();
    if (role === 'DIRECTOR') this.roleName = 'Diretor';
    else if (role === 'TEACHER') this.roleName = 'Professor';
    else if (role === 'ADMIN') this.roleName = 'Administrativo';
    else this.roleName = 'Visitante';
  }

  goBack(): void {
    const role = this.auth.getRoleFromToken();
    if (role === 'TEACHER') {
      this.router.navigate(['/academico']);
    } else {
      this.router.navigate(['/admin']);
    }
  }

  goToLogin(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
