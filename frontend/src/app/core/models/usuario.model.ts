export type CargoNivel = 1 | 2 | 3;

export interface Usuario {
  idUsuario: number;
  nome: string | null;
  telefone: string | null;
  email: string;
  cargo: number | null;
  endereco?: string | null;
}

export interface UsuarioCreatePayload {
  nome: string;
  telefone: string | null;
  email: string;
  senha: string;
  cargo: CargoNivel;
  endereco?: string | null;
}

export interface UsuarioUpdatePayload {
  nome: string;
  telefone: string | null;
  cargo: CargoNivel;
  endereco?: string | null;
}
