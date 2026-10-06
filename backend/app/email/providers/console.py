import logging
import re

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"(token=)([^&\s]+)")


def _mask_tokens(body: str) -> str:
    return _TOKEN_RE.sub(lambda match: match.group(1) + match.group(2)[:8] + "...", body)


def send(to_email: str, subject: str, body: str) -> None:
    masked_body = _mask_tokens(body)
    if masked_body == body:
        logger.warning(
            "Nenhum provedor de e-mail configurado; mensagem para %s não enviada",
            to_email,
        )
        return
    logger.info("E-mail para %s: %s", to_email, masked_body)
