import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { sessionInterceptor } from './session.interceptor';

describe('sessionInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([sessionInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    document.cookie = 'abaco_csrf=csrf-token-123; path=/';
  });

  afterEach(() => {
    httpMock.verify();
    document.cookie = 'abaco_csrf=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
  });

  it('envia cookies em requisições da API', () => {
    http.get('/api/v1/turmas').subscribe();

    const req = httpMock.expectOne('/api/v1/turmas');
    expect(req.request.withCredentials).toBe(true);
    expect(req.request.headers.has('X-CSRF-Token')).toBe(false);
    req.flush([]);
  });

  it('envia X-CSRF-Token em métodos que alteram estado', () => {
    http.post('/api/v1/turmas', {}).subscribe();

    const req = httpMock.expectOne('/api/v1/turmas');
    expect(req.request.withCredentials).toBe(true);
    expect(req.request.headers.get('X-CSRF-Token')).toBe('csrf-token-123');
    req.flush({});
  });
});
