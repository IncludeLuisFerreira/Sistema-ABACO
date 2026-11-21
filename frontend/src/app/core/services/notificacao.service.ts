import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, OnDestroy, signal } from '@angular/core';
import { Observable, catchError, finalize, map, of, tap } from 'rxjs';

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
    this.carregandoLista = true;
    this.carregando.set(true);
    this.erro.set(null);
    const params = new HttpParams().set('limite', LIMITE_PAGINA).set('offset', offset);

    return this.http.get<Notificacao[]>(this.baseUrl, { params }).pipe(
      tap((itens) => {
        const ordenados = [...itens].sort(
          (a, b) => new Date(b.criadaEm).getTime() - new Date(a.criadaEm).getTime(),
        );
        this.notificacoes.set(append ? [...this.notificacoes(), ...ordenados] : ordenados);
        this.temMais.set(itens.length === LIMITE_PAGINA);
      }),
      catchError((err: unknown) => {
        this.registrarErro(err, 'Não foi possível carregar as notificações.');
        return of([]);
      }),
      finalize(() => {
        this.carregandoLista = false;
        this.carregando.set(false);
      }),
    );
  }

  carregarContagem(): Observable<number | null> {
    if (this.contagemEmAndamento) {
      return of(null);
    }
    this.contagemEmAndamento = true;

    return this.http.get<NotificacaoContagem>(`${this.baseUrl}/contagem`).pipe(
      map(({ naoLidas }) => naoLidas),
      tap((naoLidas) => this.naoLidas.set(naoLidas)),
      catchError((err: unknown) => {
        this.registrarErro(err, 'Não foi possível carregar a contagem de notificações.');
        return of(null);
      }),
      finalize(() => {
        this.contagemEmAndamento = false;
      }),
    );
  }

  marcarLida(id: number): Observable<Notificacao | null> {
    const anterior = this.notificacoes().find((item) => item.idNotificacao === id);
    const eraNaoLida = anterior ? !anterior.lida : true;

    return this.http.patch<Notificacao>(`${this.baseUrl}/${id}/lida`, {}).pipe(
      tap((atualizada) => {
        this.notificacoes.update((itens) =>
          itens.map((item) => (item.idNotificacao === id ? atualizada : item)),
        );
        if (eraNaoLida) {
          this.naoLidas.update((total) => Math.max(0, total - 1));
        }
      }),
      catchError((err: unknown) => {
        this.registrarErro(err, 'Não foi possível marcar a notificação como lida.');
        return of(null);
      }),
    );
  }

  marcarTodas(): Observable<MarcarTodasLidasResponse | null> {
    return this.http.post<MarcarTodasLidasResponse>(`${this.baseUrl}/marcar-todas-lidas`, {}).pipe(
      tap(({ atualizadas }) => {
        this.notificacoes.update((itens) => itens.map((item) => ({ ...item, lida: true })));
        this.naoLidas.set(0);
        this.erro.set(null);
        return atualizadas;
      }),
      catchError((err: unknown) => {
        this.registrarErro(err, 'Não foi possível marcar todas as notificações como lidas.');
        return of(null);
      }),
    );
  }

  iniciarPolling(ms = 30000): void {
    if (this.pollTimer !== null) {
      return;
    }
    this.carregarContagem().subscribe();
    this.pollTimer = setInterval(() => {
      this.carregarContagem().subscribe();
    }, ms);
  }

  pararPolling(): void {
    if (this.pollTimer !== null) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  ngOnDestroy(): void {
    this.pararPolling();
  }

  private registrarErro(err: unknown, fallback: string): void {
    const mensagem = getApiErrorMessage(err, fallback);
    this.erro.set(mensagem);
    this.toast.error(mensagem);
  }
}
