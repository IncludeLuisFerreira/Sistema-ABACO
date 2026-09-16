export interface PresencaAlunoInfo {
  idAluno: number;
  nome: string | null;
}

export interface PresencaMatriculaInfo {
  idMatricula: number;
  aluno: PresencaAlunoInfo | null;
}

export interface Presenca {
  idPresenca: number;
  idMatricula: number;
  dataAula: string | null;
  presente: boolean | null;
  matricula: PresencaMatriculaInfo | null;
}

export interface PresencaItem {
  idMatricula: number;
  presente: boolean;
}

export interface PresencaBatchPayload {
  idTurma: number;
  dataAula: string;
  presencas: PresencaItem[];
}
