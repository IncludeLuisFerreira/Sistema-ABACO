import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, ValidatorFn } from '@angular/forms';

import { PASSWORD_VALIDATORS } from '../../validators/password.validator';
import { PasswordField } from './password-field';

describe('PasswordField', () => {
  let fixture: ComponentFixture<PasswordField>;
  let component: PasswordField;

  const render = (value: string, validators: ValidatorFn[] = PASSWORD_VALIDATORS): void => {
    fixture = TestBed.createComponent(PasswordField);
    component = fixture.componentInstance;
    component.control = new FormControl(value, validators);
    fixture.detectChanges();
  };

  const errorText = (): string | null =>
    fixture.nativeElement.querySelector('.field-error')?.textContent?.trim() ?? null;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [PasswordField] }).compileComponents();
  });

  it('nao exibe mensagem antes do usuario interagir', () => {
    render('');

    expect(errorText()).toBeNull();
  });

  it('exibe a mensagem no template depois de touched', () => {
    render('');
    component.control.markAsTouched();
    fixture.detectChanges();

    expect(errorText()).toBe('Senha é obrigatória');
  });

  it('exibe a mensagem quando o usuario digita uma senha invalida', () => {
    render('senhaforte');
    component.control.markAsDirty();
    fixture.detectChanges();

    expect(errorText()).toBe('A senha deve conter letras e números');
  });

  it('informa o tamanho minimo', () => {
    render('senha');
    component.control.markAsDirty();
    fixture.detectChanges();

    expect(errorText()).toBe('A senha deve ter no mínimo 8 caracteres');
  });

  it('pluraliza o tamanho minimo no singular', () => {
    const stub = new PasswordField();
    stub.control = {
      errors: { minlength: { requiredLength: 1, actualLength: 0 } },
      dirty: true,
      touched: false,
    };

    expect(stub.errorMessage).toBe('A senha deve ter no mínimo 1 caractere');
  });

  it('usa fallback para erros desconhecidos', () => {
    render('qualquer', [(control) => (control.value === 'qualquer' ? { outroErro: true } : null)]);
    component.control.markAsDirty();
    fixture.detectChanges();

    expect(errorText()).toBe('Senha inválida');
  });

  it('associa a mensagem ao input para leitores de tela', () => {
    render('');
    component.control.markAsTouched();
    fixture.detectChanges();

    const input: HTMLInputElement = fixture.nativeElement.querySelector('input');
    expect(input.getAttribute('aria-invalid')).toBe('true');
    expect(input.getAttribute('aria-describedby')).toBe(`${component.fieldId}-error`);
    expect(fixture.nativeElement.querySelector('.field-error')?.id).toBe(
      `${component.fieldId}-error`,
    );
  });
});
