def build_reset_message(settings, reset_token: str) -> tuple[str, str, str, str]:
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"

    subject = "SGA ABACO - Recuperação de Senha"
    body = f"""\
Olá,

Você solicitou a recuperação de senha no sistema SGA ABACO.

Clique no link abaixo para redefinir sua senha:
{reset_link}

Este link é válido por {settings.reset_token_expire_minutes} minutos.

Se você não solicitou esta recuperação, ignore este e-mail.

Atenciosamente,
Equipe SGA ABACO
"""
    return subject, body, reset_link, "Link de recuperação"


def build_first_access_message(settings, first_access_token: str) -> tuple[str, str, str, str]:
    first_access_link = f"{settings.frontend_url}/first-access?token={first_access_token}"

    subject = "SGA ABACO - Conta criada com sucesso"
    body = f"""\
Olá,

Seu acesso ao sistema SGA ABACO foi criado.

Por segurança, defina sua senha pessoal no primeiro acesso clicando no link abaixo:
{first_access_link}

Este link é válido por {settings.first_access_token_expire_minutes} minutos.

Caso não reconheça este cadastro, ignore este e-mail.

Atenciosamente,
Equipe SGA ABACO
"""
    return subject, body, first_access_link, "Link de primeiro acesso"
