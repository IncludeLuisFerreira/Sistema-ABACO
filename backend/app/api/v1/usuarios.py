from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.usuario_schema import UsuarioCreateSchema, UsuarioResponseSchema, UsuarioUpdateSchema
from app.services.usuario_service import (
	UsuarioEmailAlreadyExistsError,
	UsuarioHasDependenciesError,
	UsuarioNotFoundError,
	create_usuario,
	delete_usuario,
	get_usuario_by_id,
	list_usuarios,
	update_usuario,
)

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


def _guarda_anti_escalacao_admin(
	_current_user: dict,
	*,
	cargo_atual: int | None = None,
	novo_cargo: int | None = None,
	alvo_id: int | None = None,
) -> None:
	if int(_current_user.get("cargo") or 0) != 3:
		return

	requisitante_id = int(_current_user.get("sub") or 0)

	if cargo_atual == 1:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Administrador não pode gerenciar usuários de cargo 1",
		)
	if novo_cargo == 1:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Administrador não pode atribuir cargo 1",
		)
	if alvo_id is not None and alvo_id == requisitante_id and novo_cargo is not None and novo_cargo != cargo_atual:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Administrador não pode alterar o próprio cargo",
		)


@router.get("")
def read_usuarios(_current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
	return [UsuarioResponseSchema.model_validate(usuario) for usuario in list_usuarios(db)]


@router.get("/{usuario_id}")
def read_usuario(usuario_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
	try:
		usuario = get_usuario_by_id(db, usuario_id)
	except UsuarioNotFoundError as exc:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado") from exc
	return UsuarioResponseSchema.model_validate(usuario)


@router.post("")
def create_usuarios(payload: UsuarioCreateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
	_guarda_anti_escalacao_admin(_current_user, novo_cargo=payload.cargo)
	try:
		usuario = create_usuario(db, payload)
	except UsuarioEmailAlreadyExistsError as exc:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado") from exc
	return UsuarioResponseSchema.model_validate(usuario)


@router.put("/{usuario_id}")
def update_usuarios(usuario_id: int, payload: UsuarioUpdateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
	try:
		alvo = get_usuario_by_id(db, usuario_id)
	except UsuarioNotFoundError as exc:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado") from exc

	_guarda_anti_escalacao_admin(
		_current_user,
		cargo_atual=alvo.cargo,
		novo_cargo=payload.cargo,
		alvo_id=usuario_id,
	)

	try:
		usuario = update_usuario(db, usuario_id, payload)
	except UsuarioNotFoundError as exc:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado") from exc
	except UsuarioHasDependenciesError as exc:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o usuário") from exc
	return UsuarioResponseSchema.model_validate(usuario)


@router.delete("/{usuario_id}")
def delete_usuarios(usuario_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
	# REFACTOR: regra "não excluir a si mesmo" pertence ao usuario_service
	current_user_id = int((_current_user.get("sub") or 0))
	if current_user_id == usuario_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não é possível excluir o próprio usuário")

	try:
		alvo = get_usuario_by_id(db, usuario_id)
	except UsuarioNotFoundError as exc:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado") from exc

	_guarda_anti_escalacao_admin(_current_user, cargo_atual=alvo.cargo)

	try:
		delete_usuario(db, usuario_id)
	except UsuarioNotFoundError as exc:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado") from exc
	except UsuarioHasDependenciesError as exc:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível excluir um usuário que possui turmas ou pedidos vinculados") from exc

	return {"detail": "Usuário excluído com sucesso"}