import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { UsuarioService } from './usuario.service';

describe('UsuarioService', () => {
  let service: UsuarioService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    service = TestBed.inject(UsuarioService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('maps null values from list response', () => {
    let result: unknown;

    service.list().subscribe((usuarios) => {
      result = usuarios;
    });

    const request = httpMock.expectOne('http://localhost:8000/api/v1/usuarios');
    request.flush([
      {
        idUsuario: 1,
        nome: null,
        telefone: null,
        email: 'diretoria@abaco.org',
        cargo: null,
      },
    ]);

    expect(result).toEqual([
      {
        idUsuario: 1,
        nome: '',
        telefone: '',
        email: 'diretoria@abaco.org',
        cargo: 3,
      },
    ]);
  });
});
