import { Component } from '@angular/core';
import { finalize } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss'],
})
export class Login {
  form: any;

  loading = false;
  error: string | null = null;
  showPassword = false;
  shake = false;

  constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }

  onSubmit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.error = null;
    this.shake = false;
    this.loading = true;
    this.form.disable();
    const { email, password } = this.form.value as { email: string; password: string };
    this.auth.login(email, password).pipe(
      finalize(() => {
        this.loading = false;
        this.form.enable();
      })
    ).subscribe({
      next: (res) => {
        const role = res.role;
        if (role === 'DIRECTOR') {
          this.router.navigate(['/admin']);
        } else if (role === 'ADMIN') {
          this.router.navigate(['/admin']);
        } else if (role === 'TEACHER') {
          this.router.navigate(['/academico']);
        } else {
          this.router.navigate(['/admin']);
        }
      },
      error: (err) => {
        this.error = err?.message || 'E-mail ou senha incorretos';
        this.shake = true;
        setTimeout(() => this.shake = false, 500);
      },
    });
  }
}
