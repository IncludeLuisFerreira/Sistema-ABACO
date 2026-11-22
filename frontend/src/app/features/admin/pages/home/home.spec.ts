import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { AuthService } from '../../../../core/services/auth.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { DashboardService } from '../../../dashboard/services/dashboard.service';
import { AdminHome } from './home';

describe('AdminHome', () => {
  let component: AdminHome;
  let fixture: ComponentFixture<AdminHome>;

  const kpis = {
    total_alunos_ativos: 12,
    total_turmas_vigentes: 3,
    total_pedidos_pendentes: 2,
    total_estoque_critico: 1,
  };

  const academico = {
    alunos_por_curso: [{ curso: 'Curso A', quantidade: 12 }],
    status_matriculas: [{ status: 0, quantidade: 12 }],
  };

  const logistica = {
    consumo_mes_atual: [{ item: 'Papel', quantidade: 4 }],
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminHome],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: { getRoleFromToken: vi.fn(() => 'ADMIN') },
        },
        {
          provide: DashboardService,
          useValue: {
            getKpis: vi.fn(() => of(kpis)),
            getChartAcademico: vi.fn(() => of(academico)),
            getChartLogistica: vi.fn(() => of(logistica)),
          },
        },
        { provide: NotificationService, useValue: { error: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminHome);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('renderiza os quatro KPI cards', () => {
    expect(component.loading).toBe(false);
    expect(fixture.nativeElement.querySelectorAll('.kpi-card').length).toBe(4);
  });

  it('configura os graficos com largura fluida e breakpoint 768', () => {
    expect(component.donutChart.width).toBe('100%');
    expect(component.barChart.width).toBe('100%');
    expect(component.donutResponsive[0].breakpoint).toBe(768);
    expect(component.barResponsive[0].breakpoint).toBe(768);
  });
});
