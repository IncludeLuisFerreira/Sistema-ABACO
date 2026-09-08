import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Estoque } from '../../../../core/models/estoque.model';

export interface EstoqueFormSubmit {
  nomeItem: string;
  quantidadeDisponivel: number | null;
  unidade: string | null;
  estoqueMinimo: number | null;
}

@Component({
  selector: 'app-estoque-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './estoque-form.html',
  styleUrls: ['./estoque-form.scss'],
})
export class EstoqueFormComponent implements OnChanges {
  private readonly fb = inject(FormBuilder);

  @Input() mode: 'create' | 'edit' = 'create';
  @Input() item: Estoque | null = null;
  @Input() loading = false;

  @Output() readonly save = new EventEmitter<EstoqueFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  readonly form = this.fb.nonNullable.group({
    nomeItem: ['', [Validators.required]],
    quantidadeDisponivel: [<number | null>null],
    unidade: [''],
    estoqueMinimo: [<number | null>null],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['item']) {
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
    const payload: EstoqueFormSubmit = {
      nomeItem: value.nomeItem.trim(),
      quantidadeDisponivel: value.quantidadeDisponivel ?? null,
      unidade: value.unidade.trim() || null,
      estoqueMinimo: value.estoqueMinimo ?? null,
    };

    this.save.emit(payload);
  }

  private patchForm(): void {
    if (this.mode === 'edit' && this.item) {
      this.form.reset({
        nomeItem: this.item.nomeItem ?? '',
        quantidadeDisponivel: this.item.quantidadeDisponivel ?? null,
        unidade: this.item.unidade ?? '',
        estoqueMinimo: this.item.estoqueMinimo ?? null,
      });
      return;
    }

    this.form.reset({
      nomeItem: '',
      quantidadeDisponivel: null,
      unidade: '',
      estoqueMinimo: null,
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
