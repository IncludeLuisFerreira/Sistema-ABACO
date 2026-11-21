import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal, WritableSignal } from '@angular/core';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { Notificacao } from '../../../core/models/notificacao.model';
import { NotificacaoService } from '../../../core/services/notificacao.service';
import { NotificacaoSinoComponent } from './notificacao-sino';

function notificacao(id: number, lida = false, link: string | null = null): Notificacao {
  return {
    idNotificacao: id,
    tipo: 'pedido_aprovado',
    titulo: `Notificação ${id}`,
    mensagem: 'Mensagem de teste',
    link,
    lida,
    criadaEm: '2026-03-01T10:00:00Z',
  };
}

describe('NotificacaoSinoComponent', () => {
  let fixture: ComponentFixture<NotificacaoSinoComponent>;
  let service: {
    notificacoes: WritableSignal<Notificacao[]>;
    naoLidas: WritableSignal<number>;
    carregando: WritableSignal<boolean>;
    erro: WritableSignal<string | null>;
    temMais: WritableSignal<boolean>;
    carregar: ReturnType<typeof vi.fn>;
    marcarLida: ReturnType<typeof vi.fn>;
    marcarTodas: ReturnType<typeof vi.fn>;
  };
  let router: { navigateByUrl: ReturnType<typeof vi.fn> };

  async function setup(itens: Notificacao[] = []) {
    service = {
      notificacoes: signal(itens),
      naoLidas: signal(itens.filter((item) => !item.lida).length),
      carregando: signal(false),
      erro: signal<string | null>(null),
      temMais: signal(true),
      carregar: vi.fn().mockReturnValue(of([])),
      marcarLida: vi.fn().mockImplementation((id: number) => of(notificacao(id, true))),
      marcarTodas: vi.fn().mockReturnValue(of({ atualizadas: itens.length })),
    };
    router = { navigateByUrl: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [NotificacaoSinoComponent],
      providers: [
        { provide: NotificacaoService, useValue: service },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(NotificacaoSinoComponent);
    fixture.detectChanges();
  }

  function elemento(): HTMLElement {
    return fixture.nativeElement as HTMLElement;
  }

  function botaoSino(): HTMLButtonElement {
    return elemento().querySelector('.notificacao-sino__botao') as HTMLButtonElement;
  }

  it('mostra o badge com a quantidade de não lidas e atributos acessíveis', async () => {
    await setup([notificacao(1), notificacao(2, true)]);

    expect(botaoSino().getAttribute('aria-label')).toBe('Notificações');
    expect(botaoSino().getAttribute('aria-expanded')).toBe('false');
    expect(elemento().querySelector('.notificacao-sino__badge')?.textContent?.trim()).toBe('1');
    expect(elemento().querySelector('.notificacao-sino__badge')?.getAttribute('aria-live')).toBe(
      'polite',
    );
  });

  it('abre o painel carregando as 10 mais recentes e fecha no segundo clique', async () => {
    await setup();

    botaoSino().click();
    fixture.detectChanges();
    expect(service.carregar).toHaveBeenCalledWith(0, false);
    expect(botaoSino().getAttribute('aria-expanded')).toBe('true');
    expect(elemento().querySelector('.notificacao-sino__painel')).not.toBeNull();

    botaoSino().click();
    fixture.detectChanges();
    expect(elemento().querySelector('.notificacao-sino__painel')).toBeNull();
  });

  it('lista as notificações com destaque para não lidas e carrega mais em blocos de 10', async () => {
    const itens = Array.from({ length: 10 }, (_, indice) => notificacao(indice + 1, indice > 0));
    await setup(itens);

    botaoSino().click();
    fixture.detectChanges();

    const botoes = elemento().querySelectorAll('.notificacao-sino__item');
    expect(botoes).toHaveLength(10);
    expect(botoes[0].classList).toContain('notificacao-sino__item--nao-lida');
    expect(botoes[1].classList).not.toContain('notificacao-sino__item--nao-lida');

    (elemento().querySelector('.notificacao-sino__mais') as HTMLButtonElement).click();
    expect(service.carregar).toHaveBeenLastCalledWith(10, true);
  });

  it('marca uma como lida e navega para o link', async () => {
    await setup([notificacao(5, false, '/admin/logistico/pedidos/5')]);

    botaoSino().click();
    fixture.detectChanges();
    (elemento().querySelector('.notificacao-sino__item') as HTMLButtonElement).click();

    expect(service.marcarLida).toHaveBeenCalledWith(5);
    expect(router.navigateByUrl).toHaveBeenCalledWith('/admin/logistico/pedidos/5');
  });

  it('marca todas como lidas', async () => {
    await setup([notificacao(1), notificacao(2)]);
    service.naoLidas.set(2);

    botaoSino().click();
    fixture.detectChanges();
    (elemento().querySelector('.notificacao-sino__marcar-todas') as HTMLButtonElement).click();

    expect(service.marcarTodas).toHaveBeenCalled();
  });

  it('mostra estado vazio', async () => {
    await setup();

    botaoSino().click();
    fixture.detectChanges();

    expect(elemento().textContent).toContain('Nenhuma notificação');
  });

  it('mantém o painel funcional e exibe mensagem de erro', async () => {
    await setup();
    service.erro.set('Falha de rede');

    botaoSino().click();
    fixture.detectChanges();

    expect(elemento().querySelector('.notificacao-sino__erro')?.textContent).toContain(
      'Falha de rede',
    );
  });

  it('fecha com Escape e com clique fora', async () => {
    await setup();

    botaoSino().click();
    fixture.detectChanges();
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    fixture.detectChanges();
    expect(elemento().querySelector('.notificacao-sino__painel')).toBeNull();

    botaoSino().click();
    fixture.detectChanges();
    document.body.click();
    fixture.detectChanges();
    expect(elemento().querySelector('.notificacao-sino__painel')).toBeNull();
  });
});
