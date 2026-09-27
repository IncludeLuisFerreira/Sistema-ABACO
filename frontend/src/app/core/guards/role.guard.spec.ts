import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { roleGuard } from './role.guard';

function createFakeJwt(payloadObj: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify(payloadObj));
  return `${header}.${payload}.signature`;
}

describe('roleGuard', () => {
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

  it('allows access when user cargo is in allowedCargos', () => {
    const token = createFakeJwt({ sub: '1', cargo: 1, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe(true);
  });

  it('redirects to /acesso-negado when user cargo is not in allowedCargos', () => {
    const token = createFakeJwt({ sub: '2', cargo: 2, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/acesso-negado');
    expect(result).toBe('/acesso-negado');
  });

  it('redirects to /login when no token is present', () => {
    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe('/login');
  });

  it('redirects to /login and clears token when token is expired', () => {
    const token = createFakeJwt({ sub: '1', cargo: 1, exp: Math.floor(Date.now() / 1000) - 3600 });
    localStorage.setItem('abaco_token', token);

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe('/login');
    expect(localStorage.getItem('abaco_token')).toBeNull();
  });
});
