import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { TurmaService } from './turma.service';

describe('TurmaService', () => {
  let service: TurmaService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    service = TestBed.inject(TurmaService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('list calls correct endpoint', () => {
    service.list().subscribe();
    const req = httpMock.expectOne('http://localhost:8000/api/v1/turmas');
    expect(req.request.method).toBe('GET');
    req.flush([]);
  });

  it('listMine calls /me endpoint', () => {
    service.listMine().subscribe();
    const req = httpMock.expectOne('http://localhost:8000/api/v1/turmas/me');
    expect(req.request.method).toBe('GET');
    req.flush([]);
  });
});
