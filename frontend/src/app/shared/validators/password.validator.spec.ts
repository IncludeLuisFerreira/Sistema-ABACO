import { FormControl } from '@angular/forms';

import {
  PASSWORD_CONFIRMATION_VALIDATORS,
  PASSWORD_MIN_LENGTH,
  PASSWORD_VALIDATORS,
  passwordCompositionValidator,
} from './password.validator';

describe('passwordCompositionValidator', () => {
  const validate = passwordCompositionValidator();

  it('aceita senha com letras e numeros', () => {
    expect(validate(new FormControl('Senha1234'))).toBeNull();
  });

  it('rejeita senha sem numero', () => {
    expect(validate(new FormControl('senhaforte'))).toEqual({ passwordComposition: true });
  });

  it('rejeita senha sem letra', () => {
    expect(validate(new FormControl('12345678'))).toEqual({ passwordComposition: true });
  });

  it('nao valida campo vazio (deixa para o required)', () => {
    expect(validate(new FormControl(''))).toBeNull();
  });
});

describe('PASSWORD_VALIDATORS', () => {
  it('marca senha curta sem numero com minlength e composicao', () => {
    const control = new FormControl('senha', PASSWORD_VALIDATORS);

    expect(control.errors?.['minlength'].requiredLength).toBe(PASSWORD_MIN_LENGTH);
    expect(control.errors?.['passwordComposition']).toBe(true);
  });

  it('aceita senha dentro da politica', () => {
    expect(new FormControl('Senha1234', PASSWORD_VALIDATORS).valid).toBe(true);
  });

  it('confirmacao exige preenchimento e tamanho minimo', () => {
    expect(new FormControl('', PASSWORD_CONFIRMATION_VALIDATORS).errors?.['required']).toBe(true);
    expect(
      new FormControl('curta', PASSWORD_CONFIRMATION_VALIDATORS).errors?.['minlength'],
    ).toBeTruthy();
    expect(new FormControl('Senha1234', PASSWORD_CONFIRMATION_VALIDATORS).valid).toBe(true);
  });
});
