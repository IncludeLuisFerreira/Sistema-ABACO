import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { authGuard } from './auth.guard';

function createFakeJwt(payloadObj: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify(payloadObj));
  return `${header}.${payload}.signature`;
}

describe('authGuard', () => {
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

  it('allows access for valid authenticated user', () => {
    const token = createFakeJwt({ sub: '1', cargo: 1, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));
    expect(result).toBe(true);
  });

  it('redirects to /login when no token exists', () => {
    const result = TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe('/login');
  });

  it('redirects to /login and clears token when token is expired', () => {
    const token = createFakeJwt({ sub: '1', cargo: 1, exp: Math.floor(Date.now() / 1000) - 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe('/login');
    expect(localStorage.getItem('abaco_token')).toBeNull();
  });
});
