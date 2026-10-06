import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AuthService } from '../../../../core/services/auth.service';
import { AccessDenied } from './access-denied';

describe('AccessDenied', () => {
  let fixture: ComponentFixture<AccessDenied>;
  let component: AccessDenied;
  let auth: { getRoleFromToken: ReturnType<typeof vi.fn>; logout: ReturnType<typeof vi.fn> };
  let router: { navigate: ReturnType<typeof vi.fn> };

  async function setup(role: string) {
    auth = { getRoleFromToken: vi.fn().mockReturnValue(role), logout: vi.fn() };
    router = { navigate: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [AccessDenied],
      providers: [
        { provide: AuthService, useValue: auth },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AccessDenied);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  it.each([
    ['DIRECTOR', 'Diretor'],
    ['TEACHER', 'Professor'],
    ['ADMIN', 'Admin'],
    ['GUEST', 'Visitante'],
  ])('mapeia role %s para o rótulo %s', async (role, rotulo) => {
    await setup(role);
    expect(component.roleName).toBe(rotulo);
  });

  it('goBack de TEACHER navega para /academico', async () => {
    await setup('TEACHER');
    component.goBack();
    expect(router.navigate).toHaveBeenCalledWith(['/academico']);
  });

  it.each([['DIRECTOR'], ['ADMIN']])('goBack de %s navega para /admin', async (role) => {
    await setup(role);
    component.goBack();
    expect(router.navigate).toHaveBeenCalledWith(['/admin']);
  });

  it('goBack de GUEST faz logout e navega para /login', async () => {
    await setup('GUEST');
    component.goBack();
    expect(auth.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('goToLogin limpa sessão e navega para /login', async () => {
    await setup('GUEST');
    component.goToLogin();
    expect(auth.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });
});
