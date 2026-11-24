import { signal, WritableSignal, Component, signal} from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, Routes, provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { Notificacao } from '../../../../core/models/notificacao.model';
import { AuthService } from '../../../../core/services/auth.service';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { NotificacaoService } from '../../../../core/services/notificacao.service';
import { AdminLayoutComponent } from './admin-layout';

@Component({ template: '' })
class DummyComponent {}

const rotasLogistico: Routes = [
  { path: 'admin/logistico', component: DummyComponent },
  { path: 'admin/logistico/estoque', component: DummyComponent },
  { path: 'admin/logistico/pedidos', component: DummyComponent },
  { path: '**', component: DummyComponent },
];

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
  let estoque: {
    loadAlertasCount: ReturnType<typeof vi.fn>;
    alertasCount: WritableSignal<number>;
  };

  async function setup(role: string) {
    auth = { authState: vi.fn(() => ({ role })), logout: vi.fn() };
    estoque = { loadAlertasCount: vi.fn(), alertasCount: signal(0) };
    notificacoes = mockNotificacoes();

    await TestBed.configureTestingModule({
      imports: [AdminLayoutComponent],
      providers: [
        provideRouter(rotasLogistico),
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

  it('exibe um único sino na sidebar e mantém o da topbar mobile', async () => {
    await setup('ADMIN');
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelectorAll('.admin-nav__user app-notificacao-sino')).toHaveLength(1);
    expect(el.querySelectorAll('app-notificacao-sino')).toHaveLength(2);
    expect(el.querySelector('.admin-nav__notification')).toBeNull();
  });

  it('exibe badge de estoque baixo no link Estoque com rótulo acessível', async () => {
    await setup('ADMIN');
    estoque.alertasCount.set(3);
    fixture.detectChanges();

    const link = (fixture.nativeElement as HTMLElement).querySelector(
      'a[href="/admin/logistico/estoque"]',
    );
    expect(link?.querySelector('.admin-nav__badge')?.textContent?.trim()).toBe('3');
    expect(link?.getAttribute('aria-label')).toBe('Estoque: 3 itens com estoque baixo');
  });

  it('usa singular no rótulo de estoque com um alerta', async () => {
    await setup('ADMIN');
    estoque.alertasCount.set(1);
    fixture.detectChanges();

    const link = (fixture.nativeElement as HTMLElement).querySelector(
      'a[href="/admin/logistico/estoque"]',
    );
    expect(link?.getAttribute('aria-label')).toBe('Estoque: 1 item com estoque baixo');
  });

  it('não exibe badge nem rótulo de estoque quando não há alertas', async () => {
    await setup('ADMIN');

    const link = (fixture.nativeElement as HTMLElement).querySelector(
      'a[href="/admin/logistico/estoque"]',
    );
    expect(link?.querySelector('.admin-nav__badge')).toBeNull();
    expect(link?.getAttribute('aria-label')).toBeNull();
    expect(link?.getAttribute('title')).toBeNull();
  });

  it('remove o badge quando o polling zera os alertas (transição)', async () => {
    await setup('ADMIN');
    estoque.alertasCount.set(3);
    fixture.detectChanges();

    const el = fixture.nativeElement as HTMLElement;
    const link = el.querySelector('a[href="/admin/logistico/estoque"]');
    expect(link?.querySelector('.admin-nav__badge')).not.toBeNull();

    estoque.alertasCount.set(0);
    fixture.detectChanges();

    expect(link?.querySelector('.admin-nav__badge')).toBeNull();
    expect(link?.getAttribute('aria-label')).toBeNull();
  });

  it('destaca apenas o item da rota atual na seção de logística', async () => {
    await setup('ADMIN');
    const el = fixture.nativeElement as HTMLElement;
    const links = Array.from(el.querySelectorAll<HTMLAnchorElement>('a'));
    const linkVisaoGeral = links.find((a) => a.textContent?.trim() === 'Visão Geral');
    const linkEstoque = links.find((a) => a.textContent?.trim() === 'Estoque');
    const linkPedidos = links.find((a) => a.textContent?.trim() === 'Pedidos');

    await TestBed.inject(Router).navigateByUrl('/admin/logistico/estoque');
    fixture.detectChanges();

    expect(linkVisaoGeral?.classList.contains('active')).toBe(false);
    expect(linkEstoque?.classList.contains('active')).toBe(true);
    expect(linkPedidos?.classList.contains('active')).toBe(false);
  });

  it('destaca Visão Geral somente na rota /admin/logistico', async () => {
    await setup('ADMIN');
    const el = fixture.nativeElement as HTMLElement;
    const linkVisaoGeral = Array.from(el.querySelectorAll<HTMLAnchorElement>('a')).find(
      (a) => a.textContent?.trim() === 'Visão Geral',
    );

    await TestBed.inject(Router).navigateByUrl('/admin/logistico');
    fixture.detectChanges();

    expect(linkVisaoGeral?.classList.contains('active')).toBe(true);
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
