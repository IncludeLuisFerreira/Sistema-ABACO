export interface MatriculaAlunoInfo {
  idAluno: number;
  nome: string | null;
  telefone: string | null;
}

export interface MatriculaCursoInfo {
  idCurso: number;
  nomeCurso: string;
}

export interface MatriculaTurmaInfo {
  idTurma: number;
  capacidade: number | null;
  curso: MatriculaCursoInfo | null;
}

export interface Matricula {
  idMatricula: number;
  idAluno: number;
  idTurma: number;
  dataMatricula: string | null;
  status: number | null;
  aluno: MatriculaAlunoInfo | null;
  turma: MatriculaTurmaInfo | null;
}

export interface MatriculaCreatePayload {
  idAluno: number;
  idTurma: number;
  dataMatricula: string | null;
  status: number | null;
}

export interface MatriculaUpdatePayload {
  idAluno: number | null;
  idTurma: number | null;
  dataMatricula: string | null;
  status: number | null;
}
