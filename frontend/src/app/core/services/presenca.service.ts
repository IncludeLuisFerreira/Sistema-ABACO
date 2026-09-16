import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Presenca, PresencaBatchPayload } from '../models/presenca.model';

@Injectable({ providedIn: 'root' })
export class PresencaService {
  private readonly baseUrl = '/api/v1/presencas';

  constructor(private readonly http: HttpClient) {}

  listByTurma(turmaId: number, dataAula?: string): Observable<Presenca[]> {
    let params = new HttpParams();
    if (dataAula) {
      params = params.set('dataAula', dataAula);
    }
    return this.http.get<Presenca[]>(`${this.baseUrl}/turma/${turmaId}`, { params });
  }

  create(payload: PresencaBatchPayload): Observable<Presenca[]> {
    return this.http.post<Presenca[]>(this.baseUrl, payload);
  }
}
