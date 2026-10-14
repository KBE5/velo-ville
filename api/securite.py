"""Authentification et autorisation.

À compléter : vérification d'un mot de passe contre son hachage bcrypt, création et
décodage du JWT (secret et algorithme lus dans l'environnement),
dépendances utilisateur_courant() et exiger_role("exploitant").
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from api.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET


def hash_password(plain_password: str) -> str:
    """Hache le mot de passe avant stockage en base."""

    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Compare le mot de passe saisi avec le hash stocké."""

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(username: str, role: str) -> str:
    """Crée un JWT signé contenant l'identité et le rôle."""

    now = datetime.now(timezone.utc)
    expiration = now + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Vérifie la signature et l'expiration du JWT."""

    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )

