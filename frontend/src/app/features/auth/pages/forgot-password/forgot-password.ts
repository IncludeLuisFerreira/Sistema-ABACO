import { Component } from '@angular/core';
import { finalize } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './forgot-password.html',
  styleUrls: ['./forgot-password.scss'],
})
export class ForgotPassword {
  form: any;

  loading = false;
  error: string | null = null;
  success: string | null = null;
  shake = false;

  constructor(private fb: FormBuilder, private auth: AuthService) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
    });
  }

  onSubmit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.error = null;
    this.success = null;
    this.shake = false;

    this.loading = true;
    this.form.disable();

    const { email } = this.form.value;

    this.auth.forgotPassword(email).pipe(
      finalize(() => {
        this.loading = false;
        this.form.enable();
      })
    ).subscribe({
      next: (res) => {
        this.success = res.message || 'Se o e-mail estiver cadastrado, um link de recuperação será enviado';
      },
      error: (err) => {
        this.error = err?.message || 'Erro ao processar solicitação';
        this.shake = true;
        setTimeout(() => this.shake = false, 500);
      }
    });
  }
}
