import { FormControl } from '@angular/forms';

import { personNameValidator } from './person-name.validator';

describe('personNameValidator', () => {
  const validate = personNameValidator();

  it('aceita nomes com acento e espacos', () => {
    expect(validate(new FormControl('Maria Clara'))).toBeNull();
    expect(validate(new FormControl("João D'Ávila"))).toBeNull();
  });

  it('rejeita nome curto, com numero ou simbolo', () => {
    expect(validate(new FormControl('Al'))).toEqual({ personName: true });
    expect(validate(new FormControl('Ana 2'))).toEqual({ personName: true });
    expect(validate(new FormControl('<>'))).toEqual({ personName: true });
  });
});
