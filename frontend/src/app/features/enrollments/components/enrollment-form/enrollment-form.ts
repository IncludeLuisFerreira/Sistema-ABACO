import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Aluno } from '../../../../core/models/aluno.model';
import { Matricula } from '../../../../core/models/matricula.model';
import { Turma } from '../../../../core/models/turma.model';

export interface EnrollmentFormSubmit {
  idAluno: number;
  idTurma: number;
  dataMatricula: string | null;
  status: number | null;
}

@Component({
  selector: 'app-enrollment-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './enrollment-form.html',
  styleUrls: ['./enrollment-form.scss'],
})
export class EnrollmentFormComponent implements OnChanges {
  private readonly fb = inject(FormBuilder);

  @Input() mode: 'create' | 'edit' = 'create';
  @Input() matricula: Matricula | null = null;
  @Input() alunos: Aluno[] = [];
  @Input() turmas: Turma[] = [];
  @Input() loading = false;

  @Output() readonly save = new EventEmitter<EnrollmentFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  readonly form = this.fb.nonNullable.group({
    idAluno: [0, [Validators.required, Validators.min(1)]],
    idTurma: [0, [Validators.required, Validators.min(1)]],
    dataMatricula: [''],
    status: [0],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['matricula']) {
      this.patchForm();
    }

    if (changes['loading']) {
      this.toggleFormState();
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const payload: EnrollmentFormSubmit = {
      idAluno: value.idAluno,
      idTurma: value.idTurma,
      dataMatricula: value.dataMatricula || null,
      status: value.status,
    };

    this.save.emit(payload);
  }

  private patchForm(): void {
    if (this.mode === 'edit' && this.matricula) {
      this.form.reset({
        idAluno: this.matricula.idAluno,
        idTurma: this.matricula.idTurma,
        dataMatricula: this.matricula.dataMatricula ?? '',
        status: this.matricula.status ?? 0,
      });
      return;
    }

    this.form.reset({
      idAluno: 0,
      idTurma: 0,
      dataMatricula: '',
      status: 0,
    });
  }

  private toggleFormState(): void {
    if (this.loading) {
      this.form.disable({ emitEvent: false });
      return;
    }

    this.form.enable({ emitEvent: false });
  }
}
