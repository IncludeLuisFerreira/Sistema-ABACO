interface ApiErrorLike {
  error?: { detail?: unknown };
  message?: unknown;
}

function extractDetailMessage(item: unknown): string | null {
  if (typeof item === 'string') {
    return item.trim() ? item : null;
  }
  if (item && typeof item === 'object' && 'msg' in item) {
    const msg = (item as { msg?: unknown }).msg;
    if (typeof msg === 'string' && msg.trim()) {
      return msg;
    }
  }
  return null;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  const apiError = error as ApiErrorLike | null | undefined;
  const detail = apiError?.error?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
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
