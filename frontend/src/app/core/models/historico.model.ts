export interface HistoricoNota {
  prova: number | null;
  nota: number | null;
}

export interface HistoricoPresenca {
  dataAula: string | null;
  presente: boolean | null;
}

export interface HistoricoAluno {
  idAluno: number;
  nome: string;
  dataNascimento: string | null;
  telefone: string | null;
}

export interface HistoricoTurma {
  idTurma: number;
  nomeCurso: string;
  nomeProfessor: string | null;
  dataInicio: string | null;
  dataFim: string | null;
  diasAula: string | null;
}

export interface Historico {
  idMatricula: number;
  dataMatricula: string | null;
  status: number | null;
  aluno: HistoricoAluno;
  turma: HistoricoTurma;
  notas: HistoricoNota[];
  presencas: HistoricoPresenca[];
  percentualFrequencia: number | null;
}
