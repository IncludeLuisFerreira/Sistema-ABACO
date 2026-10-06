import { Component } from '@angular/core';
import { finalize } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { PasswordField } from '../../../../shared/components/password-field/password-field';
import { PrimaryButton } from '../../../../shared/components/primary-button/primary-button';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, PasswordField, PrimaryButton],
  templateUrl: './change-password.html',
  styleUrls: ['./change-password.scss'],
})
export class ChangePassword {
  form: any;

  loading = false;
  error: string | null = null;
  success: string | null = null;

  constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) {
    this.form = this.fb.group({
      senha_atual: ['', [Validators.required]],
      nova_senha: ['', [Validators.required, Validators.minLength(8), Validators.pattern(/^(?=.*[A-Za-z])(?=.*\d).+$/)]],
      confirmar_senha: ['', [Validators.required, Validators.minLength(8)]],
    });
  }

  onSubmit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.error = null;
    this.success = null;

    const { senha_atual, nova_senha, confirmar_senha } = this.form.value;

    if (nova_senha !== confirmar_senha) {
      this.error = 'As senhas não conferem';
      return;
    }

    this.loading = true;
    this.form.disable();

    this.auth.changePassword(senha_atual, nova_senha, confirmar_senha).pipe(
      finalize(() => {
        this.loading = false;
        this.form.enable();
      })
    ).subscribe({
      next: () => {
        this.success = 'Senha alterada com sucesso! Faça login novamente com a nova senha.';
        setTimeout(() => this.auth.logoutAndRedirect(), 2000);
      },
      error: (err) => {
        this.error = err?.message || 'Erro ao alterar senha';
      }
    });
  }
}
