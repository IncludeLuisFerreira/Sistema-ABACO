import { FormControl } from '@angular/forms';

import { institutionalEmailValidator, uniqueEmailValidator } from './institutional-email.validator';

describe('institutionalEmailValidator', () => {
  const validate = institutionalEmailValidator();

  it('aceita dominio institucional', () => {
    expect(validate(new FormControl('prof@abaco.org.br'))).toBeNull();
  });

  it('aceita dominio gmail', () => {
    expect(validate(new FormControl('pessoa@gmail.com'))).toBeNull();
  });

  it('rejeita dominio externo', () => {
    expect(validate(new FormControl('pessoa@hotmail.com'))).toEqual({ institutionalEmail: true });
  });
});

describe('uniqueEmailValidator', () => {
  it('bloqueia e-mail ja cadastrado', () => {
    const validate = uniqueEmailValidator(['prof@abaco.org.br']);
    expect(validate(new FormControl('PROF@abaco.org.br'))).toEqual({ emailTaken: true });
    expect(validate(new FormControl('novo@abaco.org.br'))).toBeNull();
  });
});
