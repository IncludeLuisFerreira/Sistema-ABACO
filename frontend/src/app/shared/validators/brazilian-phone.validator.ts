import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/** Celular BR: DDD (2 dígitos) + 9 dígitos = 11 no total. Vazio é permitido. */
export function brazilianPhoneValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const raw = String(control.value ?? '').trim();
    if (!raw) {
      return null;
    }

    const digits = raw.replace(/\D/g, '');
    if (!/^[1-9]\d{10}$/.test(digits)) {
      return { brazilianPhone: true };
    }

    return null;
  };
}

export function onlyPhoneDigits(value: string): string {
  return value.replace(/\D/g, '');
}

/** Máscara (XX) XXXXX-XXXX a partir dos dígitos. */
export function formatBrazilianPhone(value: string): string {
  const digits = onlyPhoneDigits(value).slice(0, 11);
  if (!digits) {
    return '';
  }
  if (digits.length <= 2) {
    return `(${digits}`;
  }
  if (digits.length <= 7) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  }
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
}
