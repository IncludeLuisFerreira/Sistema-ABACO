import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import AUTH_ERROR_HEADERS, get_current_user
from app.db.database import get_db
from app.schemas.auth_schema import (
    ChangePasswordRequest,
    FirstAccessPasswordRequest,
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
    InvalidCurrentPasswordError,
    InvalidFirstAccessTokenError,
    InvalidResetTokenError,
    PasswordsDoNotMatchError,
    authenticate_user,
    build_login_response,
    change_password,
    process_first_access_password,
    process_forgot_password,
    process_reset_password,
)
from app.core.limiter import limiter
from app.services.email_service import send_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
# HACK: rate limit hardcoded ignora settings.rate_limit_auth
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
    # REFACTOR: build_login_response já retorna dict pronto; rewrap no router acopla
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
    except Exception as error:
        logger.error("Solicitação de recuperação não concluída por falha de envio (%s)", type(error).__name__)

    return {"message": "Se o e-mail estiver cadastrado, um link de recuperação será enviado"}


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    # REFACTOR: checagem de senhas duplicada (schema + service + router)
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


@router.post("/first-access", response_model=MessageResponse)
@limiter.limit("5/minute")
def first_access(request: Request, payload: FirstAccessPasswordRequest, db: Session = Depends(get_db)):
    try:
        process_first_access_password(db, payload.token, payload.nova_senha, payload.confirmar_senha)
    except PasswordsDoNotMatchError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="As senhas não conferem",
        )
    except InvalidFirstAccessTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de primeiro acesso inválido ou expirado",
        )

    return {"message": "Senha definida com sucesso. Você já pode fazer login."}


@router.post("/change-password", response_model=MessageResponse)
@limiter.limit("5/minute")
def change_password_route(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        change_password(
            db,
            int(current_user.get("sub") or 0),
            payload.senha_atual,
            payload.nova_senha,
            payload.confirmar_senha,
        )
    except PasswordsDoNotMatchError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="As senhas não conferem",
        )
    except InvalidCurrentPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )

    return {"message": "Senha alterada com sucesso."}