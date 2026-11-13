import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { Estoque } from '../models/estoque.model';
import { EstoqueService } from './estoque.service';

const item: Estoque = {
  idItemEstoque: 1,
  nomeItem: 'Papel A4',
  quantidadeDisponivel: 10,
  unidade: 'cx',
  estoqueMinimo: 2,
};

describe('EstoqueService', () => {
  let service: EstoqueService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    service = TestBed.inject(EstoqueService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('loadAll expõe o resultado ao chamador e atualiza o estado compartilhado', () => {
    let resultado: Estoque[] | undefined;
    let estado: Estoque[] | undefined;

    service.loadAll().subscribe((items) => (resultado = items));
    service.estoque$.subscribe((items) => (estado = items));

    const req = httpMock.expectOne('/api/v1/estoque');
    expect(req.request.method).toBe('GET');
    req.flush([item]);

    expect(resultado).toEqual([item]);
    expect(estado).toEqual([item]);
  });

  it('loadAll propaga erro de rede para o chamador', () => {
    let erro: unknown;

    service.loadAll().subscribe({ error: (err) => (erro = err) });

    const req = httpMock.expectOne('/api/v1/estoque');
    req.flush({}, { status: 500, statusText: 'Server Error' });

    expect(erro).toBeTruthy();
  });
});
