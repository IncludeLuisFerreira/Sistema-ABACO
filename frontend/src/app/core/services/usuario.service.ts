import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import {
  Usuario,
  UsuarioCreatePayload,
  UsuarioUpdatePayload,
} from '../models/usuario.model';

@Injectable({ providedIn: 'root' })
export class UsuarioService {
  private readonly baseUrl = '/api/v1/usuarios';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(this.baseUrl).pipe(map((usuarios) => usuarios.map((usuario) => this.normalize(usuario))));
  }

  create(payload: UsuarioCreatePayload): Observable<Usuario> {
    return this.http.post<Usuario>(this.baseUrl, payload).pipe(map((usuario) => this.normalize(usuario)));
  }

  update(usuarioId: number, payload: UsuarioUpdatePayload): Observable<Usuario> {
    return this.http
      .put<Usuario>(`${this.baseUrl}/${usuarioId}`, payload)
      .pipe(map((usuario) => this.normalize(usuario)));
  }

  delete(usuarioId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${usuarioId}`);
  }

  private normalize(usuario: Usuario): Usuario {
    return {
      ...usuario,
      nome: usuario.nome ?? '',
      telefone: usuario.telefone ?? '',
      cargo: usuario.cargo ?? 3,
    };
  }
}
