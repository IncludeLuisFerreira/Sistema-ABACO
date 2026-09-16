import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ChartAcademico, ChartLogistica, Kpis } from '../models/dashboard.model';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly baseUrl = '/api/v1/dashboard';

  constructor(private readonly http: HttpClient) {}

  getKpis(): Observable<Kpis> {
    return this.http.get<Kpis>(`${this.baseUrl}/kpis`);
  }

  getChartAcademico(): Observable<ChartAcademico> {
    return this.http.get<ChartAcademico>(`${this.baseUrl}/charts/academico`);
  }

  getChartLogistica(): Observable<ChartLogistica> {
    return this.http.get<ChartLogistica>(`${this.baseUrl}/charts/logistica`);
  }
}
