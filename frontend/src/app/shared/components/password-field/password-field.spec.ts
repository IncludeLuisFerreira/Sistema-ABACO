import { FormControl, ValidatorFn, Validators } from '@angular/forms';

import { PasswordField } from './password-field';

const SENHA_FORTE = /^(?=.*[A-Za-z])(?=.*\d).+$/;

describe('PasswordField.errorMessage', () => {
  function campo(value: string, extras: ValidatorFn[] = []): PasswordField {
    const component = new PasswordField();
    component.control = new FormControl(value, [Validators.required, ...extras]);
    return component;
  }

  it('sem mensagem quando o controle esta valido', () => {
    const component = campo('Senha1234', [Validators.minLength(8), Validators.pattern(SENHA_FORTE)]);
    expect(component.errorMessage).toBeNull();
  });

  it('acusa senha obrigatoria quando vazio', () => {
    expect(campo('').errorMessage).toBe('Senha é obrigatória');
  });

  it('acusa tamanho minimo quando preenchido e curto', () => {
    const component = campo('senha', [Validators.minLength(8)]);
    expect(component.errorMessage).toBe('A senha deve ter no mínimo 8 caracteres');
  });

  it('acusa composicao quando falta numero', () => {
    const component = campo('senhaforte', [Validators.minLength(8), Validators.pattern(SENHA_FORTE)]);
    expect(component.errorMessage).toBe('A senha deve conter letras e números');
  });
});
