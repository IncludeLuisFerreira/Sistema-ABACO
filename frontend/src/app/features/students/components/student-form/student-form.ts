import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Aluno } from '../../../../core/models/aluno.model';

export interface StudentFormSubmit {
  nome: string;
  telefone: string | null;
  dataNascimento: string | null;
  rua: string | null;
  bairro: string | null;
  numero: number | null;
}

@Component({
  selector: 'app-student-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './student-form.html',
  styleUrls: ['./student-form.scss'],
})
export class StudentFormComponent implements OnChanges {
  private readonly fb = inject(FormBuilder);

  @Input() mode: 'create' | 'edit' = 'create';
  @Input() aluno: Aluno | null = null;
  @Input() loading = false;

  @Output() readonly save = new EventEmitter<StudentFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  readonly form = this.fb.nonNullable.group({
    nome: ['', [Validators.required]],
    telefone: [''],
    dataNascimento: [''],
    rua: [''],
    bairro: [''],
    numero: [<number | null>null],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['aluno']) {
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
    const payload: StudentFormSubmit = {
      nome: value.nome.trim(),
      telefone: value.telefone.trim() || null,
      dataNascimento: value.dataNascimento || null,
      rua: value.rua.trim() || null,
      bairro: value.bairro.trim() || null,
      numero: value.numero ?? null,
    };

    this.save.emit(payload);
  }

  private patchForm(): void {
    if (this.mode === 'edit' && this.aluno) {
      this.form.reset({
        nome: this.aluno.nome ?? '',
        telefone: this.aluno.telefone ?? '',
        dataNascimento: this.aluno.dataNascimento ?? '',
        rua: this.aluno.rua ?? '',
        bairro: this.aluno.bairro ?? '',
        numero: this.aluno.numero ?? null,
      });
      return;
    }

    this.form.reset({
      nome: '',
      telefone: '',
      dataNascimento: '',
      rua: '',
      bairro: '',
      numero: null,
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
