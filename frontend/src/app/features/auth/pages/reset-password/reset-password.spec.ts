import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../../../core/services/auth.service';
import { ResetPassword } from './reset-password';

describe('ResetPassword', () => {
  let component: ResetPassword;
  let fixture: ComponentFixture<ResetPassword>;
  let token: string | null;

  const auth = {
    resetPassword: vi.fn((resetToken: string, password: string, confirmation: string) =>
      of({ message: 'Senha redefinida' })
    ),
  };

  const makeToken = (claims: Record<string, unknown>): string =>
    `header.${btoa(JSON.stringify(claims))}.signature`;

  const createComponent = async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [ResetPassword],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { queryParamMap: convertToParamMap({ token }) } },
        },
        { provide: AuthService, useValue: auth },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ResetPassword);
    component = fixture.componentInstance;
    fixture.detectChanges();
  };

  beforeEach(() => {
    token = null;
    auth.resetPassword.mockReset();
    auth.resetPassword.mockReturnValue(of({ message: 'Senha redefinida' }));
  });

  it('blocks submission when the token is missing', async () => {
    await createComponent();

    component.onSubmit();

    expect(component.tokenValid).toBe(false);
    expect(component.error).toBe('Token de recuperação não encontrado');
    expect(auth.resetPassword).not.toHaveBeenCalled();
  });

  it('blocks an expired token', async () => {
    token = makeToken({
      sub: 'user@abaco.org.br',
      type: 'password_reset',
      exp: Math.floor(Date.now() / 1000) - 60,
    });
    await createComponent();

    component.form.setValue({ nova_senha: 'senha1234', confirmar_senha: 'senha1234' });
    component.onSubmit();

    expect(component.tokenValid).toBe(false);
    expect(component.error).toBe('Token de recuperação inválido ou expirado');
    expect(auth.resetPassword).not.toHaveBeenCalled();
  });

  it('blocks a malformed token', async () => {
    token = 'malformed-token';
    await createComponent();

    expect(component.tokenValid).toBe(false);
    expect(component.error).toBe('Token de recuperação inválido ou expirado');
  });

  it('blocks a wrong-type token', async () => {
    token = makeToken({
      sub: 'user@abaco.org.br',
      type: 'first_access',
      exp: Math.floor(Date.now() / 1000) + 600,
    });
    await createComponent();

    expect(component.tokenValid).toBe(false);
    expect(component.error).toBe('Token de recuperação inválido ou expirado');
  });

  it('does not submit a password that does not meet the requirements', async () => {
    token = makeToken({
      sub: 'user@abaco.org.br',
      type: 'password_reset',
      exp: Math.floor(Date.now() / 1000) + 600,
    });
    await createComponent();
    component.form.setValue({ nova_senha: 'abcdefgh', confirmar_senha: 'abcdefgh' });

    component.onSubmit();

    expect(component.form.controls.nova_senha.invalid).toBe(true);
    expect(auth.resetPassword).not.toHaveBeenCalled();
  });

  it('submits matching passwords for a valid token', async () => {
    token = makeToken({
      sub: 'user@abaco.org.br',
      type: 'password_reset',
      exp: Math.floor(Date.now() / 1000) + 600,
    });
    await createComponent();
    component.form.setValue({ nova_senha: 'senha1234', confirmar_senha: 'senha1234' });

    component.onSubmit();

    expect(auth.resetPassword).toHaveBeenCalledWith(token, 'senha1234', 'senha1234');
    expect(component.success).toContain('Senha redefinida com sucesso');
  });

  it('shows the backend error for an invalid reset token', async () => {
    token = makeToken({
      sub: 'user@abaco.org.br',
      type: 'password_reset',
      exp: Math.floor(Date.now() / 1000) + 600,
    });
    auth.resetPassword.mockReturnValue(throwError(() => ({ message: 'Token inválido ou expirado' })));
    await createComponent();
    component.form.setValue({ nova_senha: 'senha1234', confirmar_senha: 'senha1234' });

    component.onSubmit();

    expect(component.error).toBe('Token inválido ou expirado');
  });
});
