import { FormControl } from '@angular/forms';

import { uniqueEmailValidator } from './email.validator';

describe('uniqueEmailValidator', () => {
  it('bloqueia e-mail ja cadastrado', () => {
    const validate = uniqueEmailValidator(['prof@abaco.org.br']);
    expect(validate(new FormControl('PROF@abaco.org.br'))).toEqual({ emailTaken: true });
    expect(validate(new FormControl('novo@abaco.org.br'))).toBeNull();
  });

  it('nao restringe dominio e permite e-mail externo', () => {
    const validate = uniqueEmailValidator(['prof@abaco.org.br']);
    expect(validate(new FormControl('pessoa@gmail.com'))).toBeNull();
  });

  it('ignora valor vazio', () => {
    const validate = uniqueEmailValidator(['prof@abaco.org.br']);
    expect(validate(new FormControl('   '))).toBeNull();
  });
});
