import { AbstractControl, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';

export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_PATTERN = /^(?=.*[A-Za-z])(?=.*\d).+$/;

/** Exige letras e números, com chave de erro própria (`passwordComposition`). */
export function passwordCompositionValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = String(control.value ?? '');
    if (!value) {
      return null;
    }
    return PASSWORD_PATTERN.test(value) ? null : { passwordComposition: true };
  };
}

/** Política de senha compartilhada pelos formulários de primeiro acesso, redefinição e alteração. */
export const PASSWORD_VALIDATORS: ValidatorFn[] = [
  Validators.required,
  Validators.minLength(PASSWORD_MIN_LENGTH),
  passwordCompositionValidator(),
];

/** Confirmar senha exige apenas preenchimento e tamanho mínimo. */
export const PASSWORD_CONFIRMATION_VALIDATORS: ValidatorFn[] = [
  Validators.required,
  Validators.minLength(PASSWORD_MIN_LENGTH),
];
