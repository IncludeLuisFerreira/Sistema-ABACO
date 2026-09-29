export type CargoNivel = 1 | 2 | 3;

export interface Usuario {
  idUsuario: number;
  nome: string | null;
  telefone: string | null;
  email: string;
  cargo: number | null;
  endereco: string | null;
}

export interface UsuarioCreatePayload {
  nome: string;
  telefone: string;
  email: string;
  senha: string;
  cargo: CargoNivel;
  endereco: string;
}

export interface UsuarioUpdatePayload {
  nome: string;
  telefone: string;
  cargo: CargoNivel;
  endereco: string;
}
