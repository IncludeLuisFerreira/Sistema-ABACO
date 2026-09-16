export interface EstoqueItemInfo {
  idItemEstoque: number;
  nomeItem: string | null;
  unidade: string | null;
}

export interface ItemPedido {
  idItemPedido: number;
  idPedido: number;
  idItemEstoque: number | null;
  nomeItem: string | null;
  quantidade: number | null;
  precoUnitario: number | null;
  itemEstoque: EstoqueItemInfo | null;
}

export interface UsuarioPedidoInfo {
  idUsuario: number;
  nome: string | null;
}

export interface TurmaPedidoInfo {
  idTurma: number;
  capacidade: number | null;
  nomeCurso: string | null;
}

export interface Pedido {
  idPedido: number;
  idUsuario: number;
  idTurma: number;
  dataPedido: string | null;
  status: number | null;
  usuario: UsuarioPedidoInfo | null;
  turma: TurmaPedidoInfo | null;
  itens: ItemPedido[] | null;
}

export interface ItemPedidoCreatePayload {
  nomeItem: string;
  quantidade: number | null;
  idItemEstoque: number | null;
  precoUnitario: number | null;
}

export interface PedidoCreatePayload {
  idTurma: number;
  dataPedido: string | null;
  itens: ItemPedidoCreatePayload[];
}

export interface ItemPedidoCompraPayload {
  idItemPedido: number;
  quantidade: number;
}

export interface PedidoCompraPayload {
  itens: ItemPedidoCompraPayload[];
}

export const PEDIDO_STATUS = {
  SOLICITADO: 0,
  APROVADO: 1,
  COMPRADO: 2,
  ENTREGUE: 3,
} as const;

export function getPedidoStatusLabel(status: number | null): string {
  switch (status) {
    case 0: return 'Solicitado';
    case 1: return 'Aprovado';
    case 2: return 'Comprado';
    case 3: return 'Entregue';
    default: return 'Desconhecido';
  }
}

export function getPedidoStatusClass(status: number | null): string {
  switch (status) {
    case 0: return 'badge badge--pending';
    case 1: return 'badge badge--approved';
    case 2: return 'badge badge--purchased';
    case 3: return 'badge badge--delivered';
    default: return 'badge';
  }
}
