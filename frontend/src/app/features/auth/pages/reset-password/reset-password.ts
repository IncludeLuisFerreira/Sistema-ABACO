import { Component, OnInit } from '@angular/core';
import { finalize } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { PasswordField } from '../../../../shared/components/password-field/password-field';
import { PrimaryButton } from '../../../../shared/components/primary-button/primary-button';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, PasswordField, PrimaryButton],
  templateUrl: './reset-password.html',
  styleUrls: ['./reset-password.scss'],
})
export class ResetPassword implements OnInit {
  form: FormGroup<{ nova_senha: FormControl<string>; confirmar_senha: FormControl<string> }>;

  loading = false;
  error: string | null = null;
  success: string | null = null;
  token: string | null = null;
  tokenValid = false;

  constructor(private fb: FormBuilder, private auth: AuthService, private route: ActivatedRoute, private router: Router) {
    this.form = this.fb.nonNullable.group({
      nova_senha: ['', [Validators.required, Validators.minLength(8), Validators.pattern(/^(?=.*[A-Za-z])(?=.*\d).+$/)]],
      confirmar_senha: ['', [Validators.required, Validators.minLength(8)]],
    });
  }

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token');
    if (!this.token) {
      this.error = 'Token de recuperação não encontrado';
      return;
    }

    this.tokenValid = this.isUsableResetToken(this.token);
    if (!this.tokenValid) {
      this.error = 'Token de recuperação inválido ou expirado';
    }
  }

  onSubmit(): void {
    if (this.form.invalid || !this.tokenValid || !this.token) {
      this.form.markAllAsTouched();
      return;
    }
    this.error = null;
    this.success = null;

    const { nova_senha, confirmar_senha } = this.form.getRawValue();

    if (nova_senha !== confirmar_senha) {
      this.error = 'As senhas não conferem';
      return;
    }

    this.loading = true;
    this.form.disable();

    this.auth.resetPassword(this.token, nova_senha, confirmar_senha).pipe(
      finalize(() => {
        this.loading = false;
        this.form.enable();
      })
    ).subscribe({
      next: () => {
        this.success = 'Senha redefinida com sucesso! Redirecionando para o login...';
        setTimeout(() => this.router.navigate(['/login']), 2500);
      },
      error: (err) => {
        this.error = err?.message || 'Erro ao redefinir senha';
      }
    });
  }

  private isUsableResetToken(token: string): boolean {
    try {
      const segments = token.split('.');
      if (segments.length !== 3 || !segments[1]) return false;

      const encodedPayload = segments[1].replace(/-/g, '+').replace(/_/g, '/');
      const paddedPayload = encodedPayload.padEnd(Math.ceil(encodedPayload.length / 4) * 4, '=');
      const payload: unknown = JSON.parse(atob(paddedPayload));
      if (!payload || typeof payload !== 'object') return false;

      const claims = payload as { type?: unknown; sub?: unknown; exp?: unknown };
      return (
        claims.type === 'password_reset' &&
        typeof claims.sub === 'string' &&
        claims.sub.length > 0 &&
        typeof claims.exp === 'number' &&
        Number.isFinite(claims.exp) &&
        claims.exp > Date.now() / 1000
      );
    } catch {
      return false;
    }
  }
}
