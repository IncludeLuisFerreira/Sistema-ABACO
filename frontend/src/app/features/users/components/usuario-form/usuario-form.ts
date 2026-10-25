import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { CargoNivel, Usuario } from '../../../../core/models/usuario.model';
import {
  brazilianPhoneValidator,
  formatBrazilianPhone,
  onlyPhoneDigits,
} from '../../../../shared/validators/brazilian-phone.validator';
import { uniqueEmailValidator } from '../../../../shared/validators/institutional-email.validator';
import { personNameValidator } from '../../../../shared/validators/person-name.validator';

export interface UsuarioFormSubmit {
  nome: string;
  telefone: string | null;
  email: string;
  cargo: CargoNivel;
  endereco?: string | null;
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
  /** Quando false (admin), a opção Diretoria some do select. */
  @Input() canAssignDiretoria = true;
  /** E-mails já cadastrados — usados só no modo create para avisar duplicidade. */
  @Input() existingEmails: string[] = [];

  @Output() readonly save = new EventEmitter<UsuarioFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  private readonly allRoleOptions: Array<{ label: string; value: CargoNivel }> = [
    { label: 'Diretoria', value: 1 },
    { label: 'Professor', value: 2 },
    { label: 'Admin', value: 3 },
  ];

  roleOptions: Array<{ label: string; value: CargoNivel }> = [...this.allRoleOptions];

  readonly form = this.fb.nonNullable.group({
    nome: ['', [Validators.required, personNameValidator()]],
    telefone: ['', [brazilianPhoneValidator()]],
    email: ['', [Validators.required, Validators.email]],
    endereco: [''],
    cargo: [3 as CargoNivel, [Validators.required]],
    senha: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['canAssignDiretoria'] || changes['mode'] || changes['usuario']) {
      this.refreshRoleOptions();
    }

    if (changes['mode'] || changes['usuario']) {
      this.patchForm();
    } else if (changes['existingEmails'] && this.mode === 'create') {
      this.updateExistingEmailsValidator();
    }

    if (changes['loading']) {
      this.toggleFormState();
    }
  }

  onTelefoneInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    const masked = formatBrazilianPhone(input.value);
    this.form.controls.telefone.setValue(masked, { emitEvent: false });
    input.value = masked;
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const telefoneDigits = onlyPhoneDigits(value.telefone.trim());
    const payload: UsuarioFormSubmit = {
      nome: value.nome.trim().replace(/\s+/g, ' '),
      telefone: telefoneDigits || null,
      email: value.email.trim().toLowerCase(),
      endereco: value.endereco.trim() || null,
      cargo: Number(value.cargo) as CargoNivel,
    };

    if (this.mode === 'create') {
      payload.senha = value.senha;
    }

    this.save.emit(payload);
  }

  private refreshRoleOptions(): void {
    this.roleOptions = this.canAssignDiretoria
      ? [...this.allRoleOptions]
      : this.allRoleOptions.filter((option) => option.value !== 1);

    const cargoAtual = Number(this.form.controls.cargo.value);
    if (!this.canAssignDiretoria && cargoAtual === 1) {
      this.form.controls.cargo.setValue(3, { emitEvent: false });
    }
  }

  private patchForm(): void {
    if (this.mode === 'edit' && this.usuario) {
      this.form.reset({
        nome: this.usuario.nome ?? '',
        telefone: formatBrazilianPhone(this.usuario.telefone ?? ''),
        email: this.usuario.email,
        endereco: this.usuario.endereco ?? '',
        cargo: this.normalizeCargo(this.usuario.cargo),
        senha: '',
      });
      this.form.controls.email.setValidators([Validators.required, Validators.email]);
      this.form.controls.email.disable({ emitEvent: false });
      this.form.controls.senha.clearValidators();
      this.form.controls.senha.updateValueAndValidity({ emitEvent: false });
      this.form.controls.email.updateValueAndValidity({ emitEvent: false });
      this.refreshRoleOptions();
      return;
    }

    this.form.reset({
      nome: '',
      telefone: '',
      email: '',
      endereco: '',
      cargo: this.canAssignDiretoria ? 3 : 3,
      senha: '',
    });
    this.form.controls.email.enable({ emitEvent: false });
    this.form.controls.email.setValidators([
      Validators.required,
      Validators.email,
      uniqueEmailValidator(this.existingEmails),
    ]);
    this.form.controls.senha.setValidators([Validators.required]);
    this.form.controls.senha.updateValueAndValidity({ emitEvent: false });
    this.form.controls.email.updateValueAndValidity({ emitEvent: false });
    this.refreshRoleOptions();
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

  private updateExistingEmailsValidator(): void {
    this.form.controls.email.setValidators([
      Validators.required,
      Validators.email,
      uniqueEmailValidator(this.existingEmails),
    ]);
    this.form.controls.email.updateValueAndValidity({ emitEvent: false });
  }
}
