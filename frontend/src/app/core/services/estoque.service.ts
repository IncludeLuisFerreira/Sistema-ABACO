import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';

import { BaixaPayload, Estoque, EstoqueAlerta, EstoqueCreatePayload, EstoqueUpdatePayload } from '../models/estoque.model';

@Injectable({ providedIn: 'root' })
export class EstoqueService {
  private readonly baseUrl = '/api/v1/estoque';
  // REFACTOR: mesmo estado mantido em BehaviorSubject e signal (duas fontes)
  private readonly estoqueSubject = new BehaviorSubject<Estoque[]>([]);

  readonly estoque$ = this.estoqueSubject.asObservable();
  readonly alertasCount = signal(0);

  constructor(private readonly http: HttpClient) {}

  loadAll(): Observable<Estoque[]> {
    return this.http.get<Estoque[]>(this.baseUrl).pipe(
      tap((items) => this.estoqueSubject.next(items)),
    );
  }

  refresh(): void {
    this.reload();
    this.loadAlertasCount();
  }

  list(): Observable<Estoque[]> {
    return this.http.get<Estoque[]>(this.baseUrl).pipe(
      tap((items) => this.estoqueSubject.next(items)),
    );
  }

  search(term: string): Observable<Estoque[]> {
    return this.http.get<Estoque[]>(`${this.baseUrl}/search`, { params: { q: term } });
  }

  create(payload: EstoqueCreatePayload): Observable<Estoque> {
    return this.http.post<Estoque>(this.baseUrl, payload).pipe(
      tap(() => this.reload()),
    );
  }

  update(estoqueId: number, payload: EstoqueUpdatePayload): Observable<Estoque> {
    return this.http.put<Estoque>(`${this.baseUrl}/${estoqueId}`, payload).pipe(
      tap(() => this.reload()),
    );
  }

  delete(estoqueId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${estoqueId}`).pipe(
      tap(() => this.reload()),
    );
  }

  baixa(estoqueId: number, payload: BaixaPayload): Observable<Estoque> {
    return this.http.put<Estoque>(`${this.baseUrl}/${estoqueId}/baixa`, payload).pipe(
      tap(() => this.refresh()),
    );
  }

  getAlertas(): Observable<EstoqueAlerta[]> {
    return this.http.get<EstoqueAlerta[]>(`${this.baseUrl}/alertas`);
  }

  loadAlertasCount(): void {
    this.getAlertas().subscribe({
      next: (items) => this.alertasCount.set(items.length),
      error: () => this.alertasCount.set(0),
    });
  }

  private reload(): void {
    this.loadAll().subscribe({
      // A chamada principal (create/update/delete/baixa) ja informa o erro ao usuario.
      error: () => undefined,
    });
  }
}
