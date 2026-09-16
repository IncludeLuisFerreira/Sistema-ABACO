export interface Kpis {
  total_alunos_ativos: number;
  total_turmas_vigentes: number;
  total_pedidos_pendentes: number;
  total_estoque_critico: number;
}

export interface AlunosPorCurso {
  curso: string;
  quantidade: number;
}

export interface StatusMatriculas {
  status: number;
  quantidade: number;
}

export interface ChartAcademico {
  alunos_por_curso: AlunosPorCurso[];
  status_matriculas: StatusMatriculas[];
}

export interface ConsumoItem {
  item: string;
  quantidade: number;
}

export interface ChartLogistica {
  consumo_mes_atual: ConsumoItem[];
}
