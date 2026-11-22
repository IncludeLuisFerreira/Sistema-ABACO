"""normaliza nomeitem do estoque e mescla duplicatas

Revision ID: 010
Revises: 009
Create Date: 2026-11-19
"""
import logging
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


logger = logging.getLogger("alembic.runtime.migration")

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _normalizar_nome_item(value: str) -> str:
    return " ".join(value.split())


def upgrade() -> None:
    bind = op.get_bind()
    estoque = sa.table(
        "estoque",
        sa.column("iditemestoque", sa.Integer),
        sa.column("nomeitem", sa.String),
        sa.column("quantidadedisponivel", sa.Integer),
        sa.column("unidade", sa.String),
        sa.column("estoqueminimo", sa.Integer),
    )

    linhas = bind.execute(
        sa.select(
            estoque.c.iditemestoque,
            estoque.c.nomeitem,
            estoque.c.quantidadedisponivel,
            estoque.c.unidade,
            estoque.c.estoqueminimo,
        ).order_by(estoque.c.iditemestoque)
    ).mappings().all()

    grupos: dict[str, list[tuple[dict, str]]] = {}
    for linha in linhas:
        if linha["nomeitem"] is None:
            continue
        nome_normalizado = _normalizar_nome_item(linha["nomeitem"])
        grupos.setdefault(nome_normalizado.lower(), []).append((linha, nome_normalizado))

    for grupo in grupos.values():
        mantido, nome_normalizado = grupo[0]
        duplicatas = grupo[1:]

        if duplicatas:
            logger.info(
                "normaliza_estoque: mesclando %s em '%s' (mantido=%s)",
                [duplicata["iditemestoque"] for duplicata, _ in duplicatas],
                nome_normalizado,
                mantido["iditemestoque"],
            )
            unidades_grupo = {
                linha["unidade"] for linha, _ in grupo if linha["unidade"] is not None
            }
            if len(unidades_grupo) > 1:
                logger.warning(
                    "normaliza_estoque: unidades conflitantes %s em '%s'; mantendo a primeira",
                    sorted(unidades_grupo),
                    nome_normalizado,
                )

        quantidades = [
            linha["quantidadedisponivel"]
            for linha, _ in grupo
            if linha["quantidadedisponivel"] is not None
        ]
        minimos = [
            linha["estoqueminimo"]
            for linha, _ in grupo
            if linha["estoqueminimo"] is not None
        ]
        unidades = [
            linha["unidade"]
            for linha, _ in grupo
            if linha["unidade"] is not None
        ]

        for duplicata, _ in duplicatas:
            parametros = {
                "mantido": mantido["iditemestoque"],
                "duplicado": duplicata["iditemestoque"],
            }
            bind.execute(
                sa.text(
                    "UPDATE movimentacao_estoque SET iditemestoque = :mantido "
                    "WHERE iditemestoque = :duplicado"
                ),
                parametros,
            )
            bind.execute(
                sa.text(
                    "UPDATE itempedido SET iditemestoque = :mantido "
                    "WHERE iditemestoque = :duplicado"
                ),
                parametros,
            )
            bind.execute(
                sa.delete(estoque).where(
                    estoque.c.iditemestoque == duplicata["iditemestoque"]
                )
            )

        bind.execute(
            sa.update(estoque)
            .where(estoque.c.iditemestoque == mantido["iditemestoque"])
            .values(
                nomeitem=nome_normalizado,
                quantidadedisponivel=sum(quantidades) if quantidades else None,
                unidade=unidades[0] if unidades else None,
                estoqueminimo=max(minimos) if minimos else None,
            )
        )


def downgrade() -> None:
    # Limpeza de dados não é reversível.
    pass
