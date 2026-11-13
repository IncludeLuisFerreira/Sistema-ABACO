import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export const ALLOWED_EMAIL_DOMAINS = ['abaco.org.br', 'gmail.com'];

/** Exige e-mail válido de um domínio permitido (@abaco.org.br ou @gmail.com). */
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
    if (!ALLOWED_EMAIL_DOMAINS.includes(domain)) {
      return { institutionalEmail: true };
    }

    return null;
  };
}

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
