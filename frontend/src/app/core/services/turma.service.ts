import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Turma, TurmaCreatePayload, TurmaUpdatePayload } from '../models/turma.model';

@Injectable({ providedIn: 'root' })
export class TurmaService {
  private readonly baseUrl = '/api/v1/turmas';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Turma[]> {
    return this.http.get<Turma[]>(this.baseUrl);
  }

  listMine(): Observable<Turma[]> {
    return this.http.get<Turma[]>(`${this.baseUrl}/me`);
  }

  getById(turmaId: number): Observable<Turma> {
    return this.http.get<Turma>(`${this.baseUrl}/${turmaId}`);
  }

  // REFACTOR: refreshMine() só delega para listMine() e não é usado
  refreshMine(): Observable<Turma[]> {
    return this.listMine();
  }

  create(payload: TurmaCreatePayload): Observable<Turma> {
    return this.http.post<Turma>(this.baseUrl, payload);
  }

  update(turmaId: number, payload: TurmaUpdatePayload): Observable<Turma> {
    return this.http.put<Turma>(`${this.baseUrl}/${turmaId}`, payload);
  }

  delete(turmaId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${turmaId}`);
  }
}
