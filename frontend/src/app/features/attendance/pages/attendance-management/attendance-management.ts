import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Matricula } from '../../../../core/models/matricula.model';
import { Turma } from '../../../../core/models/turma.model';
import { Presenca, PresencaBatchPayload, PresencaItem } from '../../../../core/models/presenca.model';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { TurmaService } from '../../../../core/services/turma.service';
import { PresencaService } from '../../../../core/services/presenca.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { AttendanceListComponent, AttendanceStudentRow } from '../../components/attendance-list/attendance-list';

@Component({
  selector: 'app-attendance-management',
  standalone: true,
  imports: [CommonModule, AttendanceListComponent],
  templateUrl: './attendance-management.html',
  styleUrls: ['./attendance-management.scss'],
})
export class AttendanceManagementComponent implements OnInit {
  turmas: Turma[] = [];
  matriculas: Matricula[] = [];
  selectedTurma: Turma | null = null;
  dataAula = '';
  students: AttendanceStudentRow[] = [];
  presencasExistentes: Presenca[] = [];

  loadingTurmas = false;
  loadingPresencas = false;
  saving = false;
  localFeedback: string | null = null;

  readonly diasNome: Record<number, string> = {
    0: 'Domingo', 1: 'Segunda', 2: 'Terça', 3: 'Quarta',
    4: 'Quinta', 5: 'Sexta', 6: 'Sábado',
  };

  private formatDate(iso: string): string {
    const [ano, mes, dia] = iso.split('-');
    return `${dia}/${mes}/${ano}`;
  }

  get periodoLabel(): string {
    if (!this.selectedTurma) return '';
    const inicio = this.selectedTurma.dataInicio ? `de ${this.formatDate(this.selectedTurma.dataInicio)}` : '';
    const fim = this.selectedTurma.dataFim ? `ate ${this.formatDate(this.selectedTurma.dataFim)}` : '';
    return [inicio, fim].filter(Boolean).join(' ');
  }

  get diasAulaLabel(): string {
    if (!this.selectedTurma?.diasAula) return '';
    const dias = this.selectedTurma!.diasAula.split(',').map(Number);
    return dias.map((d) => this.diasNome[d] ?? '').join(', ');
  }

  get dataForaPeriodo(): boolean {
    if (!this.dataAula || !this.selectedTurma) return false;
    const [ano, mes, dia] = this.dataAula.split('-').map(Number);
    const data = new Date(ano, mes - 1, dia).getTime();

    if (this.selectedTurma.dataInicio) {
      const [iAno, iMes, iDia] = this.selectedTurma.dataInicio.split('-').map(Number);
      if (data < new Date(iAno, iMes - 1, iDia).getTime()) return true;
    }
    if (this.selectedTurma.dataFim) {
      const [fAno, fMes, fDia] = this.selectedTurma.dataFim.split('-').map(Number);
      if (data > new Date(fAno, fMes - 1, fDia).getTime()) return true;
    }
    return false;
  }

  get dataInvalida(): boolean {
    if (!this.dataAula || !this.selectedTurma?.diasAula) return false;
    const [ano, mes, dia] = this.dataAula.split('-').map(Number);
    const diaSemana = new Date(ano, mes - 1, dia).getDay();
    const diasPermitidos = this.selectedTurma.diasAula.split(',').map(Number);
    if (!diasPermitidos.includes(diaSemana)) return true;
    return this.dataForaPeriodo;
  }

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
    private readonly presencaService: PresencaService,
    private readonly notifications: NotificationService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadTurmas();
    this.loadMatriculas();
  }

  onTurmaChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const turmaId = Number(target.value);
    this.selectedTurma = this.turmas.find((t) => t.idTurma === turmaId) ?? null;
    this.students = [];
    this.presencasExistentes = [];

    if (this.selectedTurma && this.dataAula) {
      this.loadPresencas();
    }
    this.changeDetectorRef.detectChanges();
  }

  onDataAulaChange(dataAula: string): void {
    this.dataAula = dataAula;
    this.localFeedback = null;

    if (!this.dataAula || !this.selectedTurma) {
      this.students = [];
      this.presencasExistentes = [];
      this.changeDetectorRef.detectChanges();
      return;
    }

    if (this.dataInvalida) {
      this.students = [];
      this.presencasExistentes = [];
      if (this.dataForaPeriodo) {
        this.localFeedback = `Data fora do periodo da turma. Periodo: ${this.periodoLabel}.`;
      } else {
        this.localFeedback = `A turma so tem aulas nos dias: ${this.diasAulaLabel}.`;
      }
      this.changeDetectorRef.detectChanges();
      return;
    }

    this.loadPresencas();
  }

  onTogglePresenca(idMatricula: number): void {
    const student = this.students.find((s) => s.idMatricula === idMatricula);
    if (student) {
      student.presente = !student.presente;
      this.changeDetectorRef.detectChanges();
    }
  }

  onSave(): void {
    if (!this.selectedTurma || !this.dataAula || this.students.length === 0) {
      return;
    }

    if (this.dataInvalida) {
      this.localFeedback = this.dataForaPeriodo
        ? `Data fora do periodo da turma. Periodo: ${this.periodoLabel}.`
        : `A turma so tem aulas nos dias: ${this.diasAulaLabel}.`;
      return;
    }

    this.saving = true;
    this.localFeedback = null;

    const presencas: PresencaItem[] = this.students.map((s) => ({
      idMatricula: s.idMatricula,
      presente: s.presente,
    }));

    const payload: PresencaBatchPayload = {
      idTurma: this.selectedTurma.idTurma,
      dataAula: this.dataAula,
      presencas,
    };

    this.presencaService.create(payload).subscribe({
      next: () => {
        this.notifications.success('Presenças salvas com sucesso.');
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (err: HttpErrorResponse) => {
        const message = err?.error?.detail || err?.message || 'Erro ao registrar presenças.';
        this.localFeedback = message;
        this.notifications.error(message);
        this.saving = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private loadTurmas(): void {
    this.loadingTurmas = true;
    this.turmaService.list().subscribe({
      next: (turmas) => {
        this.turmas = turmas;
        this.loadingTurmas = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.loadingTurmas = false;
        this.notifications.error('Erro ao carregar turmas.');
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private loadMatriculas(): void {
    this.matriculaService.list().subscribe({
      next: (matriculas) => {
        this.matriculas = matriculas;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.notifications.error('Erro ao carregar matrículas.');
      },
    });
  }

  private loadPresencas(): void {
    if (!this.selectedTurma || !this.dataAula) {
      return;
    }

    this.loadingPresencas = true;
    this.presencaService.listByTurma(this.selectedTurma.idTurma, this.dataAula).subscribe({
      next: (presencas) => {
        this.presencasExistentes = presencas;
        this.buildStudentList();
        this.loadingPresencas = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.presencasExistentes = [];
        this.buildStudentList();
        this.loadingPresencas = false;
        this.notifications.error('Erro ao carregar presenças.');
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  // REFACTOR: montagem de alunos duplicada em notas/presenças/grades
  private buildStudentList(): void {
    if (!this.selectedTurma) {
      this.students = [];
      return;
    }

    const presencaMap = new Map<number, boolean>();
    for (const p of this.presencasExistentes) {
      if (p.presente !== null) {
        presencaMap.set(p.idMatricula, p.presente);
      }
    }

    const matriculasDaTurma = this.matriculas.filter(
      (m) => m.idTurma === this.selectedTurma!.idTurma && m.status === 0
    );

    this.students = matriculasDaTurma.map((m) => ({
      idMatricula: m.idMatricula,
      nomeAluno: m.aluno?.nome ?? 'Aluno #' + m.idMatricula,
      presente: presencaMap.has(m.idMatricula) ? presencaMap.get(m.idMatricula)! : false,
    }));
  }
}
