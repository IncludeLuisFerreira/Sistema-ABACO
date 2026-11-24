import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';

import { CargoNivel, Usuario } from '../../../../core/models/usuario.model';
import {
  brazilianPhoneValidator,
  formatBrazilianPhone,
  onlyPhoneDigits,
} from '../../../../shared/validators/brazilian-phone.validator';
import { uniqueEmailValidator } from '../../../../shared/validators/email.validator';
import { PASSWORD_VALIDATORS } from '../../../../shared/validators/password.validator';
import { personNameValidator } from '../../../../shared/validators/person-name.validator';

function cargoValidoValidator(control: AbstractControl): ValidationErrors | null {
  const cargo = Number(control.value);
  return cargo === 1 || cargo === 2 || cargo === 3 ? null : { cargoInvalido: true };
}

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

  readonly form = this.fb.group({
    nome: this.fb.nonNullable.control('', [Validators.required, personNameValidator()]),
    telefone: this.fb.nonNullable.control('', [brazilianPhoneValidator()]),
    email: this.fb.nonNullable.control('', [Validators.required, Validators.email]),
    endereco: this.fb.nonNullable.control(''),
    cargo: this.fb.control<CargoNivel | null>(3, [Validators.required, cargoValidoValidator]),
    senha: this.fb.nonNullable.control(''),
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

    if (changes['loading'] || changes['usuario'] || changes['mode'] || changes['canAssignDiretoria']) {
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
    if (this.editBlocked) return;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const cargo = this.cargoFromUsuario(value.cargo);
    if (cargo === null) {
      this.form.controls.cargo.markAsTouched();
      return;
    }

    const telefoneDigits = onlyPhoneDigits(value.telefone.trim());
    const payload: UsuarioFormSubmit = {
      nome: this.mode === 'edit' && value.nome === this.usuario?.nome
        ? value.nome : value.nome.trim().replace(/\s+/g, ' '),
      telefone: this.mode === 'edit' && telefoneDigits === onlyPhoneDigits(this.usuario?.telefone ?? '')
        ? this.usuario?.telefone ?? null : telefoneDigits || null,
      email: value.email.trim().toLowerCase(),
      endereco: value.endereco.trim() || null,
      cargo,
    };

    if (this.mode === 'create') {
      payload.senha = value.senha;
    }

    this.save.emit(payload);
  }

  get editBlocked(): boolean {
    return this.mode === 'edit' && !this.canAssignDiretoria && Number(this.usuario?.cargo) === 1;
  }

  private refreshRoleOptions(): void {
    this.roleOptions = this.canAssignDiretoria
      ? [...this.allRoleOptions]
      : this.allRoleOptions.filter((option) => option.value !== 1);
  }

  private patchForm(): void {
    this.form.controls.nome.setValidators([Validators.required, (control) =>
      this.mode === 'edit' && control.value === (this.usuario?.nome ?? '')
        ? null : personNameValidator()(control)]);
    this.form.controls.telefone.setValidators([(control) =>
      this.mode === 'edit' && onlyPhoneDigits(control.value) === onlyPhoneDigits(this.usuario?.telefone ?? '')
        ? null : brazilianPhoneValidator()(control)]);
    if (this.mode === 'edit' && this.usuario) {
      this.form.reset({
        nome: this.usuario.nome ?? '',
        telefone: formatBrazilianPhone(this.usuario.telefone ?? ''),
        email: this.usuario.email,
        endereco: this.usuario.endereco ?? '',
        cargo: this.cargoFromUsuario(this.usuario.cargo),
        senha: '',
      });
      if (this.form.controls.cargo.invalid) {
        this.form.controls.cargo.markAsTouched();
      }
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
      cargo: 3,
      senha: '',
    });
    this.form.controls.email.enable({ emitEvent: false });
    this.form.controls.email.setValidators([
      Validators.required,
      Validators.email,
      uniqueEmailValidator(this.existingEmails),
    ]);
    this.form.controls.senha.setValidators(PASSWORD_VALIDATORS);
    this.form.controls.senha.updateValueAndValidity({ emitEvent: false });
    this.form.controls.email.updateValueAndValidity({ emitEvent: false });
    this.refreshRoleOptions();
  }

  private cargoFromUsuario(cargo: number | null | string): CargoNivel | null {
    const num = Number(cargo);
    if (num === 1 || num === 2 || num === 3) {
      return num as CargoNivel;
    }

    return null;
  }

  private toggleFormState(): void {
    if (this.loading || this.editBlocked) {
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
