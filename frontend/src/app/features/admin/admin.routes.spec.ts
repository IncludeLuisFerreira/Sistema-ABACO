import { authGuard } from '../../core/guards/auth.guard';
import { adminGuard } from '../../core/guards/role.guard';
import { ADMIN_ROUTES } from './admin.routes';

describe('ADMIN_ROUTES', () => {
  const rootRoute = ADMIN_ROUTES.find((route) => route.path === '');

  it('protege toda a área admin com authGuard e adminGuard no nó pai', () => {
    expect(rootRoute).toBeDefined();
    expect(rootRoute?.canActivate).toContain(authGuard);
    expect(rootRoute?.canActivate).toContain(adminGuard);
  });

  it('expõe as rotas administrativas esperadas como filhas', () => {
    const paths = (rootRoute?.children ?? []).map((route) => route.path);
    for (const expected of [
      'home',
      'usuarios',
      'dashboard',
      'alunos',
      'cursos',
      'turmas',
      'matriculas',
      'presencas',
      'notas',
      'logistico',
    ]) {
      expect(paths).toContain(expected);
    }
  });

  it('não repete guards nos filhos (cobertos pelo guard do pai)', () => {
    const children = rootRoute?.children ?? [];
    for (const route of children) {
      expect(route.canActivate ?? []).toEqual([]);
    }
  });
});
