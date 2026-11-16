import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/** Bloqueia e-mail já cadastrado (comparação case-insensitive). */
export function uniqueEmailValidator(existingEmails: string[]): ValidatorFn {
  const taken = new Set(existingEmails.map((e) => (e ?? '').trim().toLowerCase()));

  return (control: AbstractControl): ValidationErrors | null => {
    const email = String(control.value ?? '').trim().toLowerCase();
    if (!email) {
      return null;
    }
    return taken.has(email) ? { emailTaken: true } : null;
  };
}
