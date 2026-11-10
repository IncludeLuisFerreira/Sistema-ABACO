import { describe, expect, it } from 'vitest';

import { getApiErrorMessage } from './api-error';

describe('getApiErrorMessage', () => {
  it('returns a string detail from the API', () => {
    const error = { error: { detail: 'Curso informado não existe' } };

    expect(getApiErrorMessage(error, 'fallback')).toBe('Curso informado não existe');
  });

  it('joins FastAPI validation error messages', () => {
    const error = {
      error: {
        detail: [
          { msg: 'Input should be a valid integer' },
          { msg: 'Field required' },
        ],
      },
    };

    expect(getApiErrorMessage(error, 'fallback')).toBe(
      'Input should be a valid integer; Field required',
    );
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
