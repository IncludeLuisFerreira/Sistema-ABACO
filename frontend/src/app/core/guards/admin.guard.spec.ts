import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { adminGuard } from './role.guard';

function createFakeJwt(payloadObj: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify(payloadObj));
  return `${header}.${payload}.signature`;
}

describe('adminGuard', () => {
  let mockRouter: { parseUrl: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    localStorage.clear();
    mockRouter = {
      parseUrl: vi.fn((url: string) => url as unknown as UrlTree)
    };

    TestBed.configureTestingModule({
      providers: [
        { provide: Router, useValue: mockRouter }
      ]
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('allows access for Director (cargo 1)', () => {
    const token = createFakeJwt({ sub: '1', cargo: 1, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
    expect(result).toBe(true);
  });

  it('allows access for Admin (cargo 3)', () => {
    const token = createFakeJwt({ sub: '3', cargo: 3, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
    expect(result).toBe(true);
  });

  it('redirects Professor (cargo 2) to /acesso-negado', () => {
    const token = createFakeJwt({ sub: '2', cargo: 2, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/acesso-negado');
    expect(result).toBe('/acesso-negado');
  });

  it('redirects unauthenticated user to /login', () => {
    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe('/login');
  });
});
