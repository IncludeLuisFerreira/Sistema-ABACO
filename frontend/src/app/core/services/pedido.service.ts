import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Pedido, PedidoCompraPayload, PedidoCreatePayload } from '../models/pedido.model';

@Injectable({ providedIn: 'root' })
export class PedidoService {
  private readonly baseUrl = '/api/v1/pedidos';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Pedido[]> {
    return this.http.get<Pedido[]>(this.baseUrl);
  }

  create(payload: PedidoCreatePayload): Observable<Pedido> {
    return this.http.post<Pedido>(this.baseUrl, payload);
  }

  aprovar(pedidoId: number): Observable<Pedido> {
    return this.http.put<Pedido>(`${this.baseUrl}/${pedidoId}/aprovar`, {});
  }

  comprar(pedidoId: number, payload: PedidoCompraPayload): Observable<Pedido> {
    return this.http.put<Pedido>(`${this.baseUrl}/${pedidoId}/comprar`, payload);
  }

  entregar(pedidoId: number): Observable<Pedido> {
    return this.http.put<Pedido>(`${this.baseUrl}/${pedidoId}/entregar`, {});
  }

  delete(pedidoId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${pedidoId}`);
  }
}
