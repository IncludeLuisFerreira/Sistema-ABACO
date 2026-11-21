import { describe, expect, it } from 'vitest';

import { getApiErrorMessage } from './api-error';

describe('getApiErrorMessage', () => {
  it('returns a string detail from the API', () => {
    const error = { error: { detail: 'Curso informado não existe' } };

    expect(getApiErrorMessage(error, 'fallback')).toBe('Curso informado não existe');
  });

  it('joins and translates FastAPI validation error messages', () => {
    const error = {
      error: {
        detail: [{ msg: 'Input should be a valid integer' }, { msg: 'Field required' }],
      },
    };

    expect(getApiErrorMessage(error, 'fallback')).toBe(
      'Informe um número inteiro válido.; Campo obrigatório.',
    );
  });

  it('translates numeric range validation messages', () => {
    const error = {
      error: {
        detail: [
          { msg: 'Input should be greater than or equal to 0' },
          { msg: 'Input should be less than or equal to 10' },
        ],
      },
    };

    expect(getApiErrorMessage(error, 'fallback')).toBe(
      'O valor deve ser maior ou igual a 0.; O valor deve ser menor ou igual a 10.',
    );
  });

  it('removes the Value error prefix from custom validators', () => {
    const error = { error: { detail: [{ msg: 'Value error, Status deve ser 0, 1 ou 2' }] } };

    expect(getApiErrorMessage(error, 'fallback')).toBe('Status deve ser 0, 1 ou 2');
  });

  it('accepts a single validation detail object', () => {
    const error = { error: { detail: { msg: 'Campo inválido' } } };

    expect(getApiErrorMessage(error, 'fallback')).toBe('Campo inválido');
  });

  it('falls back to the error message when detail is absent', () => {
    expect(getApiErrorMessage({ message: 'Http failure response' }, 'fallback')).toBe(
      'Http failure response',
    );
  });

  it('returns the fallback when detail is empty', () => {
    expect(getApiErrorMessage({ error: { detail: [] } }, 'fallback')).toBe('fallback');
    expect(getApiErrorMessage({ error: { detail: '   ' } }, 'fallback')).toBe('fallback');
    expect(getApiErrorMessage(null, 'fallback')).toBe('fallback');
  });
});
