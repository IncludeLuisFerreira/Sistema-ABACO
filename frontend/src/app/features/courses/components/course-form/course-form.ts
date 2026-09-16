import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Curso } from '../../../../core/models/curso.model';

export interface CourseFormSubmit {
  nomeCurso: string;
}

@Component({
  selector: 'app-course-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './course-form.html',
  styleUrls: ['./course-form.scss'],
})
export class CourseFormComponent implements OnChanges {
  private readonly fb = inject(FormBuilder);

  @Input() mode: 'create' | 'edit' = 'create';
  @Input() curso: Curso | null = null;
  @Input() loading = false;

  @Output() readonly save = new EventEmitter<CourseFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  readonly form = this.fb.nonNullable.group({
    nomeCurso: ['', [Validators.required]],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['curso']) {
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
    const payload: CourseFormSubmit = {
      nomeCurso: value.nomeCurso.trim(),
    };

    this.save.emit(payload);
  }

  private patchForm(): void {
    if (this.mode === 'edit' && this.curso) {
      this.form.reset({
        nomeCurso: this.curso.nomeCurso ?? '',
      });
      return;
    }

    this.form.reset({
      nomeCurso: '',
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
