import { signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { Notificacao } from '../../../../core/models/notificacao.model';
import { AuthService } from '../../../../core/services/auth.service';
import { NotificacaoService } from '../../../../core/services/notificacao.service';
import { AcademicoLayoutComponent } from './academico-layout';

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

describe('AcademicoLayoutComponent', () => {
  let fixture: ComponentFixture<AcademicoLayoutComponent>;
  let auth: { authState: ReturnType<typeof vi.fn>; logout: ReturnType<typeof vi.fn> };
  let notificacoes: ReturnType<typeof mockNotificacoes>;

  async function setup() {
    auth = { authState: vi.fn(() => ({ role: 'TEACHER' })), logout: vi.fn() };
    notificacoes = mockNotificacoes();

    await TestBed.configureTestingModule({
      imports: [AcademicoLayoutComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: auth },
        { provide: NotificacaoService, useValue: notificacoes },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AcademicoLayoutComponent);
    fixture.detectChanges();
  }

  it('exibe o sino de notificações na sidebar e na topbar mobile', async () => {
    await setup();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelectorAll('app-notificacao-sino')).toHaveLength(2);
  });

  it('marca do topbar mobile leva para a home e fecha o menu', async () => {
    await setup();
    const el = fixture.nativeElement as HTMLElement;
    const brand = el.querySelector('.mobile-topbar__brand');

    expect(brand?.tagName).toBe('A');
    expect(brand?.getAttribute('href')).toBe('/academico');
    expect(brand?.getAttribute('aria-label')).toBe('Ir para a página inicial');
    expect(brand?.querySelector('img')?.getAttribute('alt')).toBe('ABACO');

    fixture.componentInstance.menuOpen = true;
    brand?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    fixture.detectChanges();

    expect(fixture.componentInstance.menuOpen).toBe(false);
  });

  it('inicia o polling de 30 s ao entrar e limpa o estado ao sair', async () => {
    await setup();
    expect(notificacoes.iniciarPolling).toHaveBeenCalledWith(30000);

    fixture.destroy();
    expect(notificacoes.limpar).toHaveBeenCalled();
  });

  it('limpa o estado das notificações no logout', async () => {
    await setup();
    const router = TestBed.inject(Router);
    const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);

    fixture.componentInstance.logout();

    expect(notificacoes.limpar).toHaveBeenCalled();
    expect(auth.logout).toHaveBeenCalled();
    expect(navigate).toHaveBeenCalledWith(['/login']);
  });
});
