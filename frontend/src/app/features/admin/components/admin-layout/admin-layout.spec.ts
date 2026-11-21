import { signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { Notificacao } from '../../../../core/models/notificacao.model';
import { AuthService } from '../../../../core/services/auth.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { NotificacaoService } from '../../../../core/services/notificacao.service';
import { AdminLayoutComponent } from './admin-layout';

function mockNotificacoes() {
  return {
    notificacoes: signal<Notificacao[]>([]),
    naoLidas: signal(0),
    carregando: signal(false),
    erro: signal<string | null>(null),
    temMais: signal(true),
    carregar: vi.fn().mockReturnValue(of([])),
    marcarLida: vi.fn().mockReturnValue(of(null)),
    marcarTodas: vi.fn().mockReturnValue(of(null)),
    iniciarPolling: vi.fn(),
    pararPolling: vi.fn(),
    limpar: vi.fn(),
  };
}

describe('AdminLayoutComponent (menu de gestão)', () => {
  let fixture: ComponentFixture<AdminLayoutComponent>;
  let auth: { authState: ReturnType<typeof vi.fn>; logout: ReturnType<typeof vi.fn> };
  let notificacoes: ReturnType<typeof mockNotificacoes>;

  async function setup(role: string) {
    auth = { authState: vi.fn(() => ({ role })), logout: vi.fn() };
    const estoque = { loadAlertasCount: vi.fn(), alertasCount: () => 0 };
    notificacoes = mockNotificacoes();

    await TestBed.configureTestingModule({
      imports: [AdminLayoutComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: auth },
        { provide: EstoqueService, useValue: estoque },
        { provide: NotificacaoService, useValue: notificacoes },
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

  it('logo da sidebar leva para a página inicial', async () => {
    await setup('ADMIN');
    const brand = (fixture.nativeElement as HTMLElement).querySelector('.admin-nav__brand');
    expect(brand?.tagName).toBe('A');
    expect(brand?.getAttribute('href')).toBe('/admin/home');
  });

  it('exibe o sino de notificações na sidebar e na topbar mobile', async () => {
    await setup('ADMIN');
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelectorAll('app-notificacao-sino')).toHaveLength(2);
  });

  it('inicia o polling de 30 s ao entrar e limpa o estado ao sair', async () => {
    await setup('ADMIN');
    expect(notificacoes.iniciarPolling).toHaveBeenCalledWith(30000);

    fixture.destroy();
    expect(notificacoes.limpar).toHaveBeenCalled();
  });

  it('limpa o estado das notificações no logout', async () => {
    await setup('ADMIN');
    const router = TestBed.inject(Router);
    const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);

    fixture.componentInstance.logout();

    expect(notificacoes.limpar).toHaveBeenCalled();
    expect(auth.logout).toHaveBeenCalled();
    expect(navigate).toHaveBeenCalledWith(['/login']);
  });
});
