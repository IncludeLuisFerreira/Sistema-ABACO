export interface Estoque {
  idItemEstoque: number;
  nomeItem: string | null;
  quantidadeDisponivel: number | null;
  unidade: string | null;
  estoqueMinimo: number | null;
}

export interface EstoqueCreatePayload {
  nomeItem: string;
  quantidadeDisponivel: number | null;
  unidade: string | null;
  estoqueMinimo: number | null;
}

export interface EstoqueUpdatePayload {
  nomeItem: string | null;
  quantidadeDisponivel: number | null;
  unidade: string | null;
  estoqueMinimo: number | null;
}

export interface BaixaPayload {
  quantidade: number;
  justificativa: string;
}

export interface EstoqueAlerta {
  idItemEstoque: number;
  nomeItem: string | null;
  quantidadeDisponivel: number | null;
  unidade: string | null;
  estoqueMinimo: number | null;
}
