export interface Curso {
  idCurso: number;
  nomeCurso: string;
}

export interface CursoCreatePayload {
  nomeCurso: string;
}

export interface CursoUpdatePayload {
  nomeCurso: string;
}
