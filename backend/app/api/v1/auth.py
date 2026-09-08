from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import AUTH_ERROR_HEADERS
from app.db.database import get_db
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenResponse,
    UsuarioResponse,
)
from app.services.auth_service import (
    EmailNotFoundError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    PasswordsDoNotMatchError,
    authenticate_user,
    build_login_response,
    process_forgot_password,
    process_reset_password,
)
from app.core.limiter import limiter
from app.services.email_service import send_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        usuario = authenticate_user(db, payload.email, payload.senha)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers=AUTH_ERROR_HEADERS,
        )

    response = build_login_response(usuario)
    response["usuario"] = UsuarioResponse(**response["usuario"])
    return response


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        token = process_forgot_password(db, payload.email)
    except EmailNotFoundError:
        return {"message": "Se o e-mail estiver cadastrado, um link de recuperação será enviado"}

    try:
        send_reset_email(payload.email, token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar e-mail de recuperação. Tente novamente mais tarde.",
        )

    return {"message": "Se o e-mail estiver cadastrado, um link de recuperação será enviado"}


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if payload.nova_senha != payload.confirmar_senha:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="As senhas não conferem",
        )

    try:
        process_reset_password(db, payload.token, payload.nova_senha, payload.confirmar_senha)
    except InvalidResetTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )

    return {"message": "Senha redefinida com sucesso. Você já pode fazer login com a nova senha."}