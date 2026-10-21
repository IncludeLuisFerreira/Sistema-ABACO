import { FormControl } from '@angular/forms';

import {
  brazilianPhoneValidator,
  formatBrazilianPhone,
  onlyPhoneDigits,
} from './brazilian-phone.validator';

describe('brazilianPhoneValidator', () => {
  const validate = brazilianPhoneValidator();

  it('aceita campo vazio', () => {
    expect(validate(new FormControl(''))).toBeNull();
    expect(validate(new FormControl(null))).toBeNull();
  });

  it('aceita celular com DDD + 9 digitos', () => {
    expect(validate(new FormControl('11999999999'))).toBeNull();
    expect(validate(new FormControl('(11) 99999-9999'))).toBeNull();
  });

  it('rejeita telefone incompleto ou com DDD invalido', () => {
    expect(validate(new FormControl('1199999999'))).toEqual({ brazilianPhone: true });
    expect(validate(new FormControl('01999999999'))).toEqual({ brazilianPhone: true });
    expect(validate(new FormControl('abc'))).toEqual({ brazilianPhone: true });
  });

  it('onlyPhoneDigits remove mascara', () => {
    expect(onlyPhoneDigits('(11) 98888-7777')).toBe('11988887777');
  });

  it('formatBrazilianPhone aplica mascara', () => {
    expect(formatBrazilianPhone('11988887777')).toBe('(11) 98888-7777');
    expect(formatBrazilianPhone('11')).toBe('(11');
  });
});
