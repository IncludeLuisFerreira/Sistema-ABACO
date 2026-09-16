export interface NotaAlunoInfo {
  idAluno: number;
  nome: string | null;
}

export interface NotaTurmaInfo {
  idTurma: number;
  nomeCurso: string | null;
}

export interface NotaMatriculaInfo {
  idMatricula: number;
  aluno: NotaAlunoInfo | null;
  turma: NotaTurmaInfo | null;
}

export interface Nota {
  idNota: number;
  idMatricula: number;
  nota: number | null;
  prova: number | null;
  matricula: NotaMatriculaInfo | null;
}

export interface NotaItem {
  idMatricula: number;
  nota: number | null;
}

export interface NotaBatchPayload {
  idTurma: number;
  prova: number;
  notas: NotaItem[];
}

export interface MediaProva {
  prova: number;
  media: number | null;
}

export interface MediaTurma {
  idTurma: number;
  medias: MediaProva[];
}
