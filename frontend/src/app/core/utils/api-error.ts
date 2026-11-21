interface ApiErrorLike {
  error?: { detail?: unknown };
  message?: unknown;
}

interface ValidationMessageTranslation {
  pattern: RegExp;
  replacement: string;
}

const VALIDATION_MESSAGE_TRANSLATIONS: ValidationMessageTranslation[] = [
  { pattern: /^Value error,\s*/i, replacement: '' },
  {
    pattern: /^Input should be greater than or equal to (-?\d+(?:\.\d+)?)$/i,
    replacement: 'O valor deve ser maior ou igual a $1.',
  },
  {
    pattern: /^Input should be less than or equal to (-?\d+(?:\.\d+)?)$/i,
    replacement: 'O valor deve ser menor ou igual a $1.',
  },
  {
    pattern: /^Input should be greater than (-?\d+(?:\.\d+)?)$/i,
    replacement: 'O valor deve ser maior que $1.',
  },
  {
    pattern: /^Input should be less than (-?\d+(?:\.\d+)?)$/i,
    replacement: 'O valor deve ser menor que $1.',
  },
  {
    pattern: /^Input should be a valid integer$/i,
    replacement: 'Informe um número inteiro válido.',
  },
  {
    pattern: /^Input should be a valid number$/i,
    replacement: 'Informe um número válido.',
  },
  {
    pattern: /^Input should be a valid string$/i,
    replacement: 'Informe um texto válido.',
  },
  { pattern: /^Field required$/i, replacement: 'Campo obrigatório.' },
  {
    pattern: /^String should have at least (\d+) characters$/i,
    replacement: 'Deve ter ao menos $1 caracteres.',
  },
  {
    pattern: /^String should have at most (\d+) characters$/i,
    replacement: 'Deve ter no máximo $1 caracteres.',
  },
];

function translateValidationMessage(message: string): string {
  const trimmed = message.trim();
  for (const { pattern, replacement } of VALIDATION_MESSAGE_TRANSLATIONS) {
    if (pattern.test(trimmed)) {
      return trimmed.replace(pattern, replacement);
    }
  }
  return trimmed;
}

function extractDetailMessage(item: unknown): string | null {
  if (typeof item === 'string') {
    return item.trim() ? translateValidationMessage(item) : null;
  }
  if (item && typeof item === 'object' && 'msg' in item) {
    const msg = (item as { msg?: unknown }).msg;
    if (typeof msg === 'string' && msg.trim()) {
      return translateValidationMessage(msg);
    }
  }
  return null;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  const apiError = error as ApiErrorLike | null | undefined;
  const detail = apiError?.error?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return translateValidationMessage(detail);
  }

  if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
    const message = extractDetailMessage(detail);
    if (message) {
      return message;
    }
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map(extractDetailMessage)
      .filter((message): message is string => message !== null);
    if (messages.length > 0) {
      return messages.join('; ');
    }
  }

  const message = apiError?.message;
  if (typeof message === 'string' && message.trim()) {
    return message;
  }

  return fallback;
}
