import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { MediaTurma, Nota, NotaBatchPayload } from '../models/nota.model';

@Injectable({ providedIn: 'root' })
export class NotaService {
  private readonly baseUrl = '/api/v1/notas';

  constructor(private readonly http: HttpClient) {}

  listByTurma(turmaId: number, prova?: number): Observable<Nota[]> {
    let params = new HttpParams();
    if (prova !== undefined) {
      params = params.set('prova', prova);
    }
    return this.http.get<Nota[]>(`${this.baseUrl}/turma/${turmaId}`, { params });
  }

  listByMatricula(matriculaId: number): Observable<Nota[]> {
    return this.http.get<Nota[]>(`${this.baseUrl}/matricula/${matriculaId}`);
  }

  create(payload: NotaBatchPayload): Observable<Nota[]> {
    return this.http.post<Nota[]>(this.baseUrl, payload);
  }

  getMediaTurma(turmaId: number): Observable<MediaTurma> {
    return this.http.get<MediaTurma>(`${this.baseUrl}/media/turma/${turmaId}`);
  }
}
