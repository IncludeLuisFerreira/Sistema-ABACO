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

  list(): Observable<Estoque[]> {
    return this.http.get<Estoque[]>(this.baseUrl).pipe(
      tap((items) => this.estoqueSubject.next(items)),
    );
  }

  search(term: string): Observable<Estoque[]> {
    return this.http.get<Estoque[]>(`${this.baseUrl}/search`, { params: { q: term } });
  }

  create(payload: EstoqueCreatePayload): Observable<Estoque> {
    return this.http.post<Estoque>(this.baseUrl, payload);
  }

  update(estoqueId: number, payload: EstoqueUpdatePayload): Observable<Estoque> {
    return this.http.put<Estoque>(`${this.baseUrl}/${estoqueId}`, payload);
  }

  delete(estoqueId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${estoqueId}`);
  }

  baixa(estoqueId: number, payload: BaixaPayload): Observable<Estoque> {
    return this.http.put<Estoque>(`${this.baseUrl}/${estoqueId}/baixa`, payload);
  }

  getAlertas(): Observable<EstoqueAlerta[]> {
    return this.http.get<EstoqueAlerta[]>(`${this.baseUrl}/alertas`).pipe(
      tap((items) => this.alertasCount.set(items.length)),
    );
  }

  loadAlertasCount(): void {
    this.getAlertas().subscribe({
      error: () => this.resetAlertasCount(),
    });
  }

  resetAlertasCount(): void {
    this.alertasCount.set(0);
  }
}
