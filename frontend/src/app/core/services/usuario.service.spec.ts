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

    const request = httpMock.expectOne('/api/v1/usuarios');
    request.flush([
      {
        idUsuario: 1,
        nome: null,
        telefone: null,
        email: 'diretoria@abaco.org',
        cargo: null,
        endereco: null,
      },
    ]);

    expect(result).toEqual([
      {
        idUsuario: 1,
        nome: '',
        telefone: '',
        email: 'diretoria@abaco.org',
        cargo: 3,
        endereco: '',
      },
    ]);
  });

  it('sends confirmacao=true when deleting a usuario', () => {
    let result: { detail: string } | undefined;
    service.delete(7).subscribe((res) => (result = res));

    const request = httpMock.expectOne((req) => req.method === 'DELETE' && req.url === '/api/v1/usuarios/7');
    expect(request.request.params.get('confirmacao')).toBe('true');
    request.flush({ detail: 'Usuário excluído com sucesso' });

    expect(result).toEqual({ detail: 'Usuário excluído com sucesso' });
  });
});
