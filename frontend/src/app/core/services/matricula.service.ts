import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Matricula, MatriculaCreatePayload, MatriculaUpdatePayload } from '../models/matricula.model';

@Injectable({ providedIn: 'root' })
export class MatriculaService {
  private readonly baseUrl = '/api/v1/matriculas';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Matricula[]> {
    return this.http.get<Matricula[]>(this.baseUrl);
  }

  listMine(): Observable<Matricula[]> {
    return this.http.get<Matricula[]>(`${this.baseUrl}/me`);
  }

  refreshList(): Observable<Matricula[]> {
    return this.list();
  }

  refreshMine(): Observable<Matricula[]> {
    return this.listMine();
  }

  create(payload: MatriculaCreatePayload): Observable<Matricula> {
    return this.http.post<Matricula>(this.baseUrl, payload);
  }

  update(matriculaId: number, payload: MatriculaUpdatePayload): Observable<Matricula> {
    return this.http.put<Matricula>(`${this.baseUrl}/${matriculaId}`, payload);
  }

  delete(matriculaId: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.baseUrl}/${matriculaId}`);
  }
}
