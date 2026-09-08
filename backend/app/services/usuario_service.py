from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreateSchema, UsuarioUpdateSchema


class UsuarioEmailAlreadyExistsError(Exception):
	pass


class UsuarioNotFoundError(Exception):
	pass


class UsuarioHasDependenciesError(Exception):
	pass


def create_usuario(db: Session, payload: UsuarioCreateSchema) -> Usuario:
	existing_usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
	if existing_usuario:
		raise UsuarioEmailAlreadyExistsError

	usuario = Usuario(
		nome=payload.nome,
		telefone=payload.telefone,
		email=payload.email,
		senha_hash=hash_password(payload.senha),
		cargo=payload.cargo,
	)
	db.add(usuario)
	db.commit()
	db.refresh(usuario)
	return usuario


def list_usuarios(db: Session) -> list[Usuario]:
	return db.query(Usuario).order_by(Usuario.nome.asc()).all()


def get_usuario_by_id(db: Session, usuario_id: int) -> Usuario:
	usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
	if not usuario:
		raise UsuarioNotFoundError
	return usuario


def update_usuario(db: Session, usuario_id: int, payload: UsuarioUpdateSchema) -> Usuario:
	usuario = get_usuario_by_id(db, usuario_id)
	usuario.nome = payload.nome
	usuario.telefone = payload.telefone
	usuario.cargo = payload.cargo

	try:
		db.commit()
	except IntegrityError as exc:
		db.rollback()
		raise UsuarioHasDependenciesError from exc

	db.refresh(usuario)
	return usuario


def delete_usuario(db: Session, usuario_id: int) -> None:
	usuario = get_usuario_by_id(db, usuario_id)
	db.delete(usuario)

	try:
		db.commit()
	except IntegrityError as exc:
		db.rollback()
		raise UsuarioHasDependenciesError from exc