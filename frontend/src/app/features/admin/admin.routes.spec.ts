import { ADMIN_ROUTES } from './admin.routes';
import { authGuard } from '../../core/guards/auth.guard';
import { adminGuard, directorGuard } from '../../core/guards/role.guard';

describe('ADMIN_ROUTES Security Guards Configuration', () => {
  it('root admin route contains authGuard', () => {
    const rootRoute = ADMIN_ROUTES.find((r) => r.path === '');
    expect(rootRoute).toBeDefined();
    expect(rootRoute?.canActivate).toContain(authGuard);
  });

  it('route "usuarios" requires directorGuard (cargo 1)', () => {
    const rootRoute = ADMIN_ROUTES.find((r) => r.path === '');
    const usuariosRoute = rootRoute?.children?.find((r) => r.path === 'usuarios');
    expect(usuariosRoute).toBeDefined();
    expect(usuariosRoute?.canActivate).toContain(directorGuard);
  });

  it('route "dashboard" requires directorGuard (cargo 1)', () => {
    const rootRoute = ADMIN_ROUTES.find((r) => r.path === '');
    const dashboardRoute = rootRoute?.children?.find((r) => r.path === 'dashboard');
    expect(dashboardRoute).toBeDefined();
    expect(dashboardRoute?.canActivate).toContain(directorGuard);
  });

  it('routes "alunos", "cursos", "turmas", "matriculas", "logistico" require adminGuard (cargo 1, 3)', () => {
    const rootRoute = ADMIN_ROUTES.find((r) => r.path === '');
    const children = rootRoute?.children || [];

    const protectedPaths = ['home', 'alunos', 'cursos', 'turmas', 'matriculas', 'presencas', 'notas', 'logistico'];

    for (const path of protectedPaths) {
      const route = children.find((r) => r.path === path);
      expect(route).toBeDefined();
      expect(route?.canActivate).toContain(adminGuard);
    }
  });
});
