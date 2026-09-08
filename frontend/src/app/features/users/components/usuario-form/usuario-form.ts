import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { CargoNivel, Usuario } from '../../../../core/models/usuario.model';

export interface UsuarioFormSubmit {
  nome: string;
  telefone: string | null;
  email: string;
  cargo: CargoNivel;
  senha?: string;
}

@Component({
  selector: 'app-usuario-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './usuario-form.html',
  styleUrls: ['./usuario-form.scss'],
})
export class UsuarioFormComponent implements OnChanges {
  private readonly fb = inject(FormBuilder);

  @Input() mode: 'create' | 'edit' = 'create';
  @Input() usuario: Usuario | null = null;
  @Input() loading = false;

  @Output() readonly save = new EventEmitter<UsuarioFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  readonly roleOptions: Array<{ label: string; value: CargoNivel }> = [
    { label: 'Diretoria', value: 1 },
    { label: 'Professor', value: 2 },
    { label: 'Administrativo', value: 3 },
  ];

  readonly form = this.fb.nonNullable.group({
    nome: ['', [Validators.required]],
    telefone: [''],
    email: ['', [Validators.required, Validators.email]],
    cargo: [3 as CargoNivel, [Validators.required]],
    senha: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['usuario']) {
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
    const payload: UsuarioFormSubmit = {
      nome: value.nome.trim(),
      telefone: value.telefone.trim() || null,
      email: value.email.trim(),
      cargo: Number(value.cargo) as CargoNivel,
    };

    if (this.mode === 'create') {
      payload.senha = value.senha;
    }

    this.save.emit(payload);
  }

  private patchForm(): void {
    if (this.mode === 'edit' && this.usuario) {
      this.form.reset({
        nome: this.usuario.nome ?? '',
        telefone: this.usuario.telefone ?? '',
        email: this.usuario.email,
        cargo: this.normalizeCargo(this.usuario.cargo),
        senha: '',
      });
      this.form.controls.email.disable({ emitEvent: false });
      this.form.controls.senha.clearValidators();
      this.form.controls.senha.updateValueAndValidity({ emitEvent: false });
      return;
    }

    this.form.reset({
      nome: '',
      telefone: '',
      email: '',
      cargo: 3,
      senha: '',
    });
    this.form.controls.email.enable({ emitEvent: false });
    this.form.controls.senha.setValidators([Validators.required]);
    this.form.controls.senha.updateValueAndValidity({ emitEvent: false });
  }

  private normalizeCargo(cargo: number | null | string): CargoNivel {
    const num = Number(cargo);
    if (num === 1 || num === 2 || num === 3) {
      return num as CargoNivel;
    }

    return 3;
  }

  private toggleFormState(): void {
    if (this.loading) {
      this.form.disable({ emitEvent: false });
      return;
    }

    this.form.enable({ emitEvent: false });
    if (this.mode === 'edit') {
      this.form.controls.email.disable({ emitEvent: false });
    }
  }
}
