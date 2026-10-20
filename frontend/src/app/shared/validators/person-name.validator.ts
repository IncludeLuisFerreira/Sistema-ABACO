import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

const NOME_PATTERN = /^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž' -]+$/;
const NOME_MIN_LENGTH = 3;

/** Nome com ao menos 3 caracteres: letras (com acento), espaços, hífen ou apóstrofo. */
export function personNameValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const cleaned = String(control.value ?? '').trim().replace(/\s+/g, ' ');
    if (!cleaned) {
      return null;
    }
    if (cleaned.length < NOME_MIN_LENGTH || !NOME_PATTERN.test(cleaned)) {
      return { personName: true };
    }
    return null;
  };
}
