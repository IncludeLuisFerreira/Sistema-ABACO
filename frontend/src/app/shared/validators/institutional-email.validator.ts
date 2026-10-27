import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export const ALLOWED_EMAIL_DOMAIN = 'abaco.org.br';

/** Exige e-mail válido do domínio institucional @abaco.org.br. */
export function institutionalEmailValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const email = String(control.value ?? '').trim().toLowerCase();
    if (!email) {
      return null;
    }

    const at = email.lastIndexOf('@');
    if (at < 1) {
      return { email: true };
    }

    const domain = email.slice(at + 1);
    if (domain !== ALLOWED_EMAIL_DOMAIN) {
      return { institutionalEmail: true };
    }

    return null;
  };
}

/** Bloqueia e-mail já cadastrado (comparação case-insensitive). */
export function uniqueEmailValidator(existingEmails: string[]): ValidatorFn {
  const taken = new Set(existingEmails.map((e) => e.trim().toLowerCase()));

  return (control: AbstractControl): ValidationErrors | null => {
    const email = String(control.value ?? '').trim().toLowerCase();
    if (!email) {
      return null;
    }
    return taken.has(email) ? { emailTaken: true } : null;
  };
}
