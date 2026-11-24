export interface Notificacao {
  idNotificacao: number;
  tipo: string;
  titulo: string;
  mensagem: string;
  link: string | null;
  lida: boolean;
  criadaEm: string;
}

export interface NotificacaoContagem {
  naoLidas: number;
}

export interface MarcarTodasLidasResponse {
  atualizadas: number;
}
