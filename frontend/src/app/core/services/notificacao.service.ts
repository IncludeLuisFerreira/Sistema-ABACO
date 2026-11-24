import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, OnDestroy, signal } from '@angular/core';
import { EMPTY, Observable, catchError, finalize, map, of, takeWhile, tap } from 'rxjs';

import {
  MarcarTodasLidasResponse,
  Notificacao,
  NotificacaoContagem,
} from '../models/notificacao.model';
import { getApiErrorMessage } from '../utils/api-error';
import { NotificationService } from './notification.service';

const LIMITE_PAGINA = 10;

@Injectable({ providedIn: 'root' })
export class NotificacaoService implements OnDestroy {
  private readonly baseUrl = '/api/v1/notificacoes';
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private contagemEmAndamento = false;
  private carregandoLista = false;
  private geracao = 0;
  private emProcessamento = new Set<number>();
  private falhaPollingAtiva = false;

  readonly notificacoes = signal<Notificacao[]>([]);
  readonly naoLidas = signal(0);
  readonly carregando = signal(false);
  readonly erro = signal<string | null>(null);
  readonly temMais = signal(true);

  constructor(
    private readonly http: HttpClient,
    private readonly toast: NotificationService,
  ) {}

  carregar(offset = 0, append = false): Observable<Notificacao[]> {
    if (this.carregandoLista) {
      return of([]);
    }
    const geracao = this.geracao;
    this.carregandoLista = true;
    this.carregando.set(true);
    this.erro.set(null);
    const params = new HttpParams().set('limite', LIMITE_PAGINA).set('offset', offset);

    return this.http.get<Notificacao[]>(this.baseUrl, { params }).pipe(
      takeWhile(() => geracao === this.geracao),
      tap((itens) => {
        const ordenados = [...itens].sort(
          (a, b) => new Date(b.criadaEm).getTime() - new Date(a.criadaEm).getTime(),
        );
        this.notificacoes.set(append ? [...this.notificacoes(), ...ordenados] : ordenados);
        this.temMais.set(itens.length === LIMITE_PAGINA);
      }),
      catchError((err: unknown) => {
        if (geracao !== this.geracao) {
          return EMPTY;
        }
        this.registrarErro(err, 'Não foi possível carregar as notificações.');
        return of([]);
      }),
      finalize(() => {
        if (geracao === this.geracao) {
          this.carregandoLista = false;
          this.carregando.set(false);
        }
      }),
    );
  }

  carregarContagem(): Observable<number | null> {
    return this.carregarContagemInterno(false);
  }

  marcarLida(id: number): Observable<Notificacao | null> {
    if (this.emProcessamento.has(id)) {
      return of(null);
    }
    const geracao = this.geracao;
    this.emProcessamento.add(id);

    return this.http.patch<Notificacao>(`${this.baseUrl}/${id}/lida`, {}).pipe(
      takeWhile(() => geracao === this.geracao),
      tap((atualizada) => {
        const anterior = this.notificacoes().find((item) => item.idNotificacao === id);
        this.notificacoes.update((itens) =>
          itens.map((item) => (item.idNotificacao === id ? atualizada : item)),
        );
        if (anterior && !anterior.lida) {
          this.naoLidas.update((total) => Math.max(0, total - 1));
        }
      }),
      catchError((err: unknown) => {
        if (geracao !== this.geracao) {
          return EMPTY;
        }
        this.registrarErro(err, 'Não foi possível marcar a notificação como lida.');
        return of(null);
      }),
      finalize(() => {
        if (geracao === this.geracao) {
          this.emProcessamento.delete(id);
        }
      }),
    );
  }

  marcarTodas(): Observable<MarcarTodasLidasResponse | null> {
    const geracao = this.geracao;

    return this.http.post<MarcarTodasLidasResponse>(`${this.baseUrl}/marcar-todas-lidas`, {}).pipe(
      takeWhile(() => geracao === this.geracao),
      tap(() => {
        this.notificacoes.update((itens) => itens.map((item) => ({ ...item, lida: true })));
        this.naoLidas.set(0);
        this.erro.set(null);
      }),
      catchError((err: unknown) => {
        if (geracao !== this.geracao) {
          return EMPTY;
        }
        this.registrarErro(err, 'Não foi possível marcar todas as notificações como lidas.');
        return of(null);
      }),
    );
  }

  iniciarPolling(ms = 30000): void {
    if (this.pollTimer !== null) {
      return;
    }
    this.carregarContagemInterno(true).subscribe();
    this.pollTimer = setInterval(() => {
      this.carregarContagemInterno(true).subscribe();
    }, ms);
  }

  pararPolling(): void {
    if (this.pollTimer !== null) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  limpar(): void {
    this.geracao += 1;
    this.pararPolling();
    this.notificacoes.set([]);
    this.naoLidas.set(0);
    this.carregando.set(false);
    this.erro.set(null);
    this.temMais.set(true);
    this.carregandoLista = false;
    this.contagemEmAndamento = false;
    this.emProcessamento.clear();
    this.falhaPollingAtiva = false;
  }

  ngOnDestroy(): void {
    this.limpar();
  }

  private carregarContagemInterno(doPolling: boolean): Observable<number | null> {
    if (this.contagemEmAndamento) {
      return of(null);
    }
    const geracao = this.geracao;
    this.contagemEmAndamento = true;

    return this.http.get<NotificacaoContagem>(`${this.baseUrl}/contagem`).pipe(
      takeWhile(() => geracao === this.geracao),
      map(({ naoLidas }) => naoLidas),
      tap((naoLidas) => {
        this.naoLidas.set(naoLidas);
        if (this.falhaPollingAtiva) {
          this.falhaPollingAtiva = false;
          this.erro.set(null);
        }
      }),
      catchError((err: unknown) => {
        if (geracao !== this.geracao) {
          return EMPTY;
        }
        if (!(doPolling && this.falhaPollingAtiva)) {
          if (doPolling) {
            this.falhaPollingAtiva = true;
          }
          this.registrarErro(err, 'Não foi possível carregar a contagem de notificações.');
        }
        return of(null);
      }),
      finalize(() => {
        if (geracao === this.geracao) {
          this.contagemEmAndamento = false;
        }
      }),
    );
  }

  private registrarErro(err: unknown, fallback: string): void {
    const mensagem = getApiErrorMessage(err, fallback);
    this.erro.set(mensagem);
    this.toast.error(mensagem);
  }
}
