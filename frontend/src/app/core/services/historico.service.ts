import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Historico } from '../models/historico.model';

@Injectable({ providedIn: 'root' })
export class HistoricoService {
  private readonly baseUrl = '/api/v1/historico';

  constructor(private readonly http: HttpClient) {}

  getByMatricula(matriculaId: number): Observable<Historico> {
    return this.http.get<Historico>(`${this.baseUrl}/matricula/${matriculaId}`);
  }
}
