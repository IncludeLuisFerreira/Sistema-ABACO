from app.email.exceptions import EmailDeliveryError
from app.email.service import (
    send_estoque_baixo_email,
    send_first_access_email,
    send_pedido_aprovado_email,
    send_reset_email,
)

__all__ = [
    "EmailDeliveryError",
    "send_estoque_baixo_email",
    "send_first_access_email",
    "send_pedido_aprovado_email",
    "send_reset_email",
]

