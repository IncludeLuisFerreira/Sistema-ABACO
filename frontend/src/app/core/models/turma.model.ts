export interface TurmaCursoInfo {
  idCurso: number;
  nomeCurso: string;
}

export interface TurmaProfessorInfo {
  idUsuario: number;
  nome: string | null;
}

export interface Avaliacao {
  nome: string;
  tipo: 'prova' | 'trabalho';
  peso: number;
}

export interface Turma {
  idTurma: number;
  capacidade: number | null;
  dataInicio: string | null;
  dataFim: string | null;
  idCurso: number;
  idProfessor: number | null;
  diasAula: string | null;
  vagasOcupadas: number | null;
  avaliacoes: Avaliacao[] | null;
  curso: TurmaCursoInfo | null;
  professor: TurmaProfessorInfo | null;
}

export interface TurmaCreatePayload {
  capacidade: number | null;
  dataInicio: string | null;
  dataFim: string | null;
  idCurso: number;
  idProfessor: number | null;
  diasAula: string | null;
  avaliacoes: Avaliacao[] | null;
}

export interface TurmaUpdatePayload {
  capacidade: number | null;
  dataInicio: string | null;
  dataFim: string | null;
  idCurso: number | null;
  idProfessor: number | null;
  diasAula: string | null;
  avaliacoes: Avaliacao[] | null;
}
