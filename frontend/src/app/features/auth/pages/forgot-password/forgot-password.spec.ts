okimport { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../../../core/services/auth.service';
import { ForgotPassword } from './forgot-password';

describe('ForgotPassword', () => {
  let component: ForgotPassword;
  let fixture: ComponentFixture<ForgotPassword>;

  const auth = {
    forgotPassword: vi.fn((email: string) =>
      of({ message: 'Se o e-mail estiver cadastrado, um link de recuperação será enviado' })
    ),
  };

  beforeEach(async () => {
    auth.forgotPassword.mockReset();
    auth.forgotPassword.mockReturnValue(
      of({ message: 'Se o e-mail estiver cadastrado, um link de recuperação será enviado' })
    );

    await TestBed.configureTestingModule({
      imports: [ForgotPassword],
      providers: [provideRouter([]), { provide: AuthService, useValue: auth }],
    }).compileComponents();

    fixture = TestBed.createComponent(ForgotPassword);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('does not submit an invalid email', () => {
    component.form.controls.email.setValue('not-an-email');

    component.onSubmit();

    expect(auth.forgotPassword).not.toHaveBeenCalled();
    expect(component.form.controls.email.touched).toBe(true);
  });

  it('requests recovery and displays the generic success message', () => {
    component.form.controls.email.setValue('user@abaco.org.br');

    component.onSubmit();

    expect(auth.forgotPassword).toHaveBeenCalledWith('user@abaco.org.br');
    expect(component.success).toContain('um link de recuperação será enviado');
  });

  it('shows an error when the request fails', () => {
    auth.forgotPassword.mockReturnValue(throwError(() => ({ message: 'Falha temporária' })));
    component.form.controls.email.setValue('user@abaco.org.br');

    component.onSubmit();

    expect(component.error).toBe('Falha temporária');
  });
});
