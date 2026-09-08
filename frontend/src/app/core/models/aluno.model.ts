export interface Aluno {
  idAluno: number;
  nome: string;
  telefone: string | null;
  dataNascimento: string | null;
  rua: string | null;
  bairro: string | null;
  numero: number | null;
}

export interface AlunoCreatePayload {
  nome: string;
  telefone: string | null;
  dataNascimento: string | null;
  rua: string | null;
  bairro: string | null;
  numero: number | null;
}

export interface AlunoUpdatePayload {
  nome: string;
  telefone: string | null;
  dataNascimento: string | null;
  rua: string | null;
  bairro: string | null;
  numero: number | null;
}
