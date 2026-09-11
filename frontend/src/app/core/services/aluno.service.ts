import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
// REFACTOR: import 'map' do rxjs não é utilizado
import { Observable, map } from 'rxjs';

import { Aluno, AlunoCreatePayload, AlunoUpdatePayload } from '../models/aluno.model';

@Injectable({ providedIn: 'root' })
export class AlunoService {
  private readonly baseUrl: string;

  constructor(private readonly http: HttpClient) {
    this.baseUrl = '/api/v1/alunos';
  }

  list(): Observable<Aluno[]> {
    return this.http.get<Aluno[]>(this.baseUrl);
  }

  create(payload: AlunoCreatePayload): Observable<Aluno> {
    return this.http.post<Aluno>(this.baseUrl, payload);
  }

  update(alunoId: number, payload: AlunoUpdatePayload): Observable<Aluno> {
    return this.http.put<Aluno>(`${this.baseUrl}/${alunoId}`, payload);
  }

  delete(alunoId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${alunoId}`);
  }
}
