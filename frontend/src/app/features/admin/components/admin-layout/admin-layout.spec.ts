import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AuthService } from '../../../../core/services/auth.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { AdminLayoutComponent } from './admin-layout';

describe('AdminLayoutComponent (menu de gestão)', () => {
  let fixture: ComponentFixture<AdminLayoutComponent>;

  async function setup(role: string) {
    const auth = { authState: () => ({ role }), logout: vi.fn() };
    const estoque = { loadAlertasCount: vi.fn(), alertasCount: () => 0 };

    await TestBed.configureTestingModule({
      imports: [AdminLayoutComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: auth },
        { provide: EstoqueService, useValue: estoque },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminLayoutComponent);
    fixture.detectChanges();
  }

  it.each([['DIRECTOR'], ['ADMIN']])('exibe o link de Usuarios para %s', async (role) => {
    await setup(role);
    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('Administracao');
    expect(text).toContain('Usuarios');
  });

  it('não exibe a seção de gestão para TEACHER', async () => {
    await setup('TEACHER');
    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).not.toContain('Usuarios');
  });
});
