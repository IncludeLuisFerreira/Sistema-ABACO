from slowapi import Limiter
from slowapi.util import get_remote_address

# TODO: limiter in-memory por IP; não compartilha entre workers nem por conta
limiter = Limiter(key_func=get_remote_address)
