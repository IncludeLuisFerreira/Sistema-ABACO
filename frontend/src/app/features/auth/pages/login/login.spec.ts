import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { AuthService } from '../../../../core/services/auth.service';
import { Login } from './login';

describe('Login', () => {
  let fixture: ComponentFixture<Login>;
  let component: Login;
  let router: Router;
  let auth: { login: ReturnType<typeof vi.fn>; logout: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    auth = { login: vi.fn(), logout: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [Login],
      providers: [provideRouter([]), { provide: AuthService, useValue: auth }],
    }).compileComponents();

    router = TestBed.inject(Router);
    vi.spyOn(router, 'navigate').mockResolvedValue(true);

    fixture = TestBed.createComponent(Login);
    component = fixture.componentInstance;
  });

  function preencherFormulario(email = 'a@b.com', password = 'senha123') {
    component.form.setValue({ email, password });
  }

  it('deve criar', () => {
    expect(component).toBeTruthy();
  });

  it('navega TEACHER para /academico', () => {
    auth.login.mockReturnValue(of({ token: 't', role: 'TEACHER' }));
    preencherFormulario();
    component.onSubmit();

    expect(router.navigate).toHaveBeenCalledWith(['/academico']);
    expect(auth.logout).not.toHaveBeenCalled();
  });

  it.each([['DIRECTOR'], ['ADMIN']])('navega %s para /admin', (role) => {
    auth.login.mockReturnValue(of({ token: 't', role }));
    preencherFormulario();
    component.onSubmit();

    expect(router.navigate).toHaveBeenCalledWith(['/admin']);
    expect(auth.logout).not.toHaveBeenCalled();
  });

  it('GUEST faz logout e vai para /acesso-negado', () => {
    auth.login.mockReturnValue(of({ token: 't', role: 'GUEST' }));
    preencherFormulario();
    component.onSubmit();

    expect(auth.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/acesso-negado']);
  });

  it('exibe erro e shake quando o login falha', () => {
    auth.login.mockReturnValue(throwError(() => ({ message: 'Credenciais inválidas' })));
    preencherFormulario();
    component.onSubmit();

    expect(component.error).toBe('Credenciais inválidas');
    expect(component.shake).toBe(true);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('formulário inválido não chama o backend', () => {
    preencherFormulario('', '');
    component.onSubmit();

    expect(auth.login).not.toHaveBeenCalled();
  });
});
