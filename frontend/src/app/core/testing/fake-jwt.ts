export interface FakeJwtPayload {
  sub?: string;
  cargo?: number | null;
  exp?: number;
}

const DEFAULT_FUTURE_EXP = Math.floor(Date.now() / 1000) + 3600;

function base64Url(value: object): string {
  return btoa(JSON.stringify(value)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function fakeJwt(payload: FakeJwtPayload = {}): string {
  const header = { alg: 'HS256', typ: 'JWT' };
  const body = { exp: DEFAULT_FUTURE_EXP, ...payload };
  return `${base64Url(header)}.${base64Url(body)}.assinatura-fake`;
}

export function fakeExpiredJwt(payload: FakeJwtPayload = {}): string {
  return fakeJwt({ exp: Math.floor(Date.now() / 1000) - 60, ...payload });
}
