from sqlalchemy.exc import IntegrityError


def is_unique_violation(exc: IntegrityError) -> bool:
    """Distingue violação de unicidade de outros erros de integridade.

    PostgreSQL expõe 23505 em ``orig.pgcode``; SQLite (usado nos testes) só
    informa pelo texto do erro, por isso o fallback por mensagem.
    """
    orig = getattr(exc, "orig", None)
    if getattr(orig, "pgcode", None) == "23505":
        return True
    message = str(orig or exc).lower()
    return "unique" in message or "uq_estoque_nomeitem_lower" in message
