import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { directorGuard } from './role.guard';

function createFakeJwt(payloadObj: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify(payloadObj));
  return `${header}.${payload}.signature`;
}

describe('directorGuard', () => {
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

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, {} as never));
    expect(result).toBe(true);
  });

  it('redirects Admin (cargo 3) to /acesso-negado because directorGuard strictly requires cargo 1', () => {
    const token = createFakeJwt({ sub: '3', cargo: 3, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/acesso-negado');
    expect(result).toBe('/acesso-negado');
  });

  it('redirects Professor (cargo 2) to /acesso-negado', () => {
    const token = createFakeJwt({ sub: '2', cargo: 2, exp: Math.floor(Date.now() / 1000) + 3600 });
    localStorage.setItem('abaco_token', token);

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/acesso-negado');
    expect(result).toBe('/acesso-negado');
  });

  it('redirects when no token is present to /login', () => {
    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, {} as never));
    expect(mockRouter.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe('/login');
  });
});
