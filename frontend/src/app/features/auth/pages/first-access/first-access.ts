import { Component, OnInit } from '@angular/core';
import { finalize } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { PasswordField } from '../../../../shared/components/password-field/password-field';
import { PrimaryButton } from '../../../../shared/components/primary-button/primary-button';
import { PASSWORD_CONFIRMATION_VALIDATORS, PASSWORD_VALIDATORS } from '../../../../shared/validators/password.validator';

@Component({
  selector: 'app-first-access',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, PasswordField, PrimaryButton],
  templateUrl: './first-access.html',
  styleUrls: ['./first-access.scss'],
})
export class FirstAccess implements OnInit {
  form: any;

  loading = false;
  error: string | null = null;
  success: string | null = null;
  token: string | null = null;

  constructor(private fb: FormBuilder, private auth: AuthService, private route: ActivatedRoute, private router: Router) {
    this.form = this.fb.group({
      nova_senha: ['', PASSWORD_VALIDATORS],
      confirmar_senha: ['', PASSWORD_CONFIRMATION_VALIDATORS],
    });
  }

  ngOnInit() {
    this.token = this.route.snapshot.queryParamMap.get('token');
    if (!this.token) {
      this.error = 'Token de primeiro acesso não encontrado';
    }
  }

  onSubmit() {
    if (this.form.invalid || !this.token) {
      this.form.markAllAsTouched();
      return;
    }
    this.error = null;
    this.success = null;

    const { nova_senha, confirmar_senha } = this.form.value;

    if (nova_senha !== confirmar_senha) {
      this.error = 'As senhas não conferem';
      return;
    }

    this.loading = true;
    this.form.disable();

    this.auth.firstAccess(this.token, nova_senha, confirmar_senha).pipe(
      finalize(() => {
        this.loading = false;
        this.form.enable();
      })
    ).subscribe({
      next: () => {
        this.success = 'Senha definida com sucesso! Redirecionando para o login...';
        setTimeout(() => this.router.navigate(['/login']), 2500);
      },
      error: (err) => {
        this.error = err?.message || 'Erro ao definir senha';
      }
    });
  }
}
