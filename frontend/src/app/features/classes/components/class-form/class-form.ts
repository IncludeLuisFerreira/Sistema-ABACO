import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { Curso } from '../../../../core/models/curso.model';
import { Turma } from '../../../../core/models/turma.model';
import { getStatusTurma } from '../turma-card/turma-card';
import { Usuario } from '../../../../core/models/usuario.model';

export interface ClassFormSubmit {
  capacidade: number | null;
  dataInicio: string | null;
  dataFim: string | null;
  idCurso: number;
  idProfessor: number | null;
  diasAula: string | null;
  avaliacoes: { nome: string; tipo: string; peso: number }[] | null;
}

interface DiaSemana {
  label: string;
  value: number;
}

@Component({
  selector: 'app-class-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './class-form.html',
  styleUrls: ['./class-form.scss'],
})
export class ClassFormComponent implements OnChanges {
  private readonly fb = inject(FormBuilder);

  @Input() mode: 'create' | 'edit' = 'create';
  @Input() turma: Turma | null = null;
  @Input() cursos: Curso[] = [];
  @Input() professores: Usuario[] = [];
  @Input() allTurmas: Turma[] = [];
  @Input() loading = false;

  @Output() readonly save = new EventEmitter<ClassFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  cursoContextLabel: string | null = null;
  professorContextLabel: string | null = null;
  conflitoLabel: string | null = null;

  readonly diasSemana: DiaSemana[] = [
    { label: 'Dom', value: 0 },
    { label: 'Seg', value: 1 },
    { label: 'Ter', value: 2 },
    { label: 'Qua', value: 3 },
    { label: 'Qui', value: 4 },
    { label: 'Sex', value: 5 },
    { label: 'Sab', value: 6 },
  ];

  readonly form = this.fb.nonNullable.group({
    idCurso: [0, [Validators.required, Validators.min(1)]],
    idProfessor: [0],
    capacidade: [0],
    dataInicio: [''],
    dataFim: [''],
    diasAula: this.fb.array(this.diasSemana.map(() => false)),
    avaliacoes: this.fb.array<FormGroup>([]),
  });

  get diasAulaArray(): FormArray {
    return this.form.controls.diasAula as FormArray;
  }

  get diasAulaControls(): FormControl[] {
    return (this.form.controls.diasAula as FormArray).controls as FormControl[];
  }

  get diasAulaString(): string | null {
    const selected = this.diasAulaArray.value
      .map((checked: boolean, i: number) => checked ? this.diasSemana[i].value : null)
      .filter((v: number | null) => v !== null);
    return selected.length > 0 ? selected.join(',') : null;
  }

  get avaliacoesArray(): FormArray<FormGroup> {
    return this.form.controls.avaliacoes as FormArray<FormGroup>;
  }

  addAvaliacao(): void {
    this.avaliacoesArray.push(this.fb.nonNullable.group({
      nome: [''],
      tipo: ['prova'],
      peso: [10],
    }));
  }

  removeAvaliacao(index: number): void {
    this.avaliacoesArray.removeAt(index);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['turma']) {
      this.patchForm();
    }

    if (changes['loading']) {
      this.toggleFormState();
    }
  }

  onCursoChange(): void {
    this.updateContexto();
  }

  onProfessorChange(): void {
    this.updateContexto();
  }

  updateContexto(): void {
    const cursoId = this.form.controls.idCurso.value;
    const profId = this.form.controls.idProfessor.value;
    this.cursoContextLabel = null;
    this.professorContextLabel = null;
    this.conflitoLabel = null;

    if (!cursoId) return;

    const turmasDoCurso = this.allTurmas.filter((t) => t.idCurso === Number(cursoId));
    const noSemestre = turmasDoCurso.length;
    if (noSemestre > 0) {
      const cursoNome = this.cursos.find((c) => c.idCurso === Number(cursoId))?.nomeCurso ?? 'curso';
      this.cursoContextLabel = `Já existem ${noSemestre} ${noSemestre === 1 ? 'turma' : 'turmas'} de ${cursoNome}`;
    }

    if (!profId || Number(profId) === 0) return;

    const turmasDoProf = this.allTurmas.filter((t) => t.idProfessor === Number(profId));
    if (turmasDoProf.length > 0) {
      const profNome = this.professores.find((p) => p.idUsuario === Number(profId))?.nome ?? 'professor';
      this.professorContextLabel = `${profNome} já tem ${turmasDoProf.length} ${turmasDoProf.length === 1 ? 'turma' : 'turmas'} neste semestre`;
    }

    const inicio = this.form.controls.dataInicio.value;
    const fim = this.form.controls.dataFim.value;
    const diasAulaStr = this.diasAulaString;

    if (inicio && fim && diasAulaStr && Number(profId) > 0) {
      const conflitos = this.allTurmas.filter((t) => {
        if (t.idProfessor !== Number(profId)) return false;
        if (this.mode === 'edit' && this.turma && t.idTurma === this.turma.idTurma) return false;
        if (!t.dataInicio || !t.dataFim || !t.diasAula) return false;
        const sobrepoe = inicio <= t.dataFim && fim >= t.dataInicio;
        return sobrepoe && t.diasAula === diasAulaStr;
      });

      if (conflitos.length > 0) {
        this.conflitoLabel = `Atenção: o professor já tem ${conflitos.length} ${conflitos.length === 1 ? 'turma' : 'turmas'} no mesmo período e dias`;
      }
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const payload: ClassFormSubmit = {
      idCurso: value.idCurso,
      idProfessor: value.idProfessor > 0 ? value.idProfessor : null,
      capacidade: value.capacidade > 0 ? value.capacidade : null,
      dataInicio: value.dataInicio || null,
      dataFim: value.dataFim || null,
      diasAula: this.diasAulaString,
      avaliacoes: this.avaliacoesArray.value.length > 0
        ? this.avaliacoesArray.value.map((a: { nome: string; tipo: string; peso: number }) => ({
            nome: a.nome || `Avaliação`,
            tipo: a.tipo || 'prova',
            peso: a.peso || 10,
          }))
        : null,
    };

    this.save.emit(payload);
  }

  private patchForm(): void {
    this.avaliacoesArray.clear();

    if (this.mode === 'edit' && this.turma) {
      const diasSelecionados = (this.turma.diasAula ?? '').split(',').map(Number);
      const diasArray = this.diasSemana.map((d) => diasSelecionados.includes(d.value));

      this.form.reset({
        idCurso: this.turma.idCurso,
        idProfessor: this.turma.idProfessor ?? 0,
        capacidade: this.turma.capacidade ?? 0,
        dataInicio: this.turma.dataInicio ?? '',
        dataFim: this.turma.dataFim ?? '',
      });
      this.diasAulaArray.patchValue(diasArray);

      if (this.turma.avaliacoes?.length) {
        for (const a of this.turma.avaliacoes) {
          this.avaliacoesArray.push(this.fb.nonNullable.group({
            nome: [a.nome || ''],
            tipo: [a.tipo || 'prova'],
            peso: [a.peso || 10],
          }));
        }
      }
      return;
    }

    this.form.reset({
      idCurso: 0,
      idProfessor: 0,
      capacidade: 0,
      dataInicio: '',
      dataFim: '',
    });
    this.diasAulaArray.patchValue(this.diasSemana.map(() => false));
  }

  private toggleFormState(): void {
    if (this.loading) {
      this.form.disable({ emitEvent: false });
      return;
    }

    this.form.enable({ emitEvent: false });
  }
}
