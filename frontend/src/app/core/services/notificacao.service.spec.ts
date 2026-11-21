import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { firstValueFrom } from 'rxjs';

import { Notificacao } from '../models/notificacao.model';
import { NotificationService } from './notification.service';
import { NotificacaoService } from './notificacao.service';

function notificacao(id: number, criadaEm: string, lida = false): Notificacao {
  return {
    idNotificacao: id,
    tipo: 'pedido_aprovado',
    titulo: `Pedido ${id}`,
    mensagem: 'Seu pedido foi aprovado',
    link: `/admin/logistico/pedidos/${id}`,
    lida,
    criadaEm,
  };
}

describe('NotificacaoService', () => {
  let service: NotificacaoService;
  let http: HttpTestingController;
  let toast: { error: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    toast = { error: vi.fn() };
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: NotificationService, useValue: toast },
      ],
    });
    service = TestBed.inject(NotificacaoService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    service.pararPolling();
    http.verify();
    vi.useRealTimers();
  });

  it('carrega as 10 notificações mais recentes primeiro', async () => {
    const promise = firstValueFrom(service.carregar());
    const req = http.expectOne((r) => r.url === '/api/v1/notificacoes');
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('limite')).toBe('10');
    expect(req.request.params.get('offset')).toBe('0');
    req.flush([notificacao(1, '2026-01-01T10:00:00Z'), notificacao(2, '2026-03-01T10:00:00Z')]);

    await promise;

    expect(service.notificacoes().map((item) => item.idNotificacao)).toEqual([2, 1]);
    expect(service.carregando()).toBe(false);
    expect(service.erro()).toBeNull();
  });

  it('acrescenta a próxima página e marca quando não há mais itens', async () => {
    service.notificacoes.set([notificacao(1, '2026-03-01T10:00:00Z')]);
    const promise = firstValueFrom(service.carregar(10, true));

    http
      .expectOne((r) => r.url === '/api/v1/notificacoes')
      .flush([notificacao(2, '2026-01-01T10:00:00Z')]);
    await promise;

    expect(service.notificacoes().map((item) => item.idNotificacao)).toEqual([1, 2]);
    expect(service.temMais()).toBe(false);
  });

  it('atualiza a contagem', async () => {
    const promise = firstValueFrom(service.carregarContagem());
    http.expectOne('/api/v1/notificacoes/contagem').flush({ naoLidas: 7 });

    await promise;

    expect(service.naoLidas()).toBe(7);
  });

  it('não dispara contagens concorrentes', () => {
    service.carregarContagem().subscribe();
    service.carregarContagem().subscribe();

    http.expectOne('/api/v1/notificacoes/contagem').flush({ naoLidas: 3 });
  });

  it('marca uma como lida, atualiza o item e o contador', async () => {
    service.notificacoes.set([notificacao(5, '2026-03-01T10:00:00Z')]);
    service.naoLidas.set(2);
    const promise = firstValueFrom(service.marcarLida(5));

    const req = http.expectOne('/api/v1/notificacoes/5/lida');
    expect(req.request.method).toBe('PATCH');
    req.flush(notificacao(5, '2026-03-01T10:00:00Z', true));
    await promise;

    expect(service.notificacoes()[0].lida).toBe(true);
    expect(service.naoLidas()).toBe(1);
  });

  it('marca todas como lidas e zera o badge', async () => {
    service.notificacoes.set([
      notificacao(1, '2026-03-01T10:00:00Z'),
      notificacao(2, '2026-02-01T10:00:00Z'),
    ]);
    service.naoLidas.set(2);
    const promise = firstValueFrom(service.marcarTodas());

    const req = http.expectOne('/api/v1/notificacoes/marcar-todas-lidas');
    expect(req.request.method).toBe('POST');
    req.flush({ atualizadas: 2 });
    await promise;

    expect(service.notificacoes().every((item) => item.lida)).toBe(true);
    expect(service.naoLidas()).toBe(0);
  });

  it('mostra toast e preserva notificações já carregadas em caso de erro', async () => {
    service.notificacoes.set([notificacao(1, '2026-03-01T10:00:00Z')]);
    service.naoLidas.set(4);
    const promise = firstValueFrom(service.carregar());

    http
      .expectOne((r) => r.url === '/api/v1/notificacoes')
      .flush({ detail: 'Falha de rede' }, { status: 500, statusText: 'Server Error' });
    await promise;

    expect(toast.error).toHaveBeenCalledWith('Falha de rede');
    expect(service.erro()).toBe('Falha de rede');
    expect(service.notificacoes().map((item) => item.idNotificacao)).toEqual([1]);
    expect(service.naoLidas()).toBe(4);
  });

  it('inicia o polling uma vez, não concorre e para de forma idempotente', () => {
    vi.useFakeTimers();

    service.iniciarPolling(1000);
    service.iniciarPolling(1000);
    http.expectOne('/api/v1/notificacoes/contagem').flush({ naoLidas: 1 });

    vi.advanceTimersByTime(1000);
    http.expectOne('/api/v1/notificacoes/contagem').flush({ naoLidas: 2 });

    service.pararPolling();
    service.pararPolling();
    vi.advanceTimersByTime(3000);
    http.expectNone('/api/v1/notificacoes/contagem');
  });
});
