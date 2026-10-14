"""Dépendances FastAPI pour authentification et rôles."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Utilisateur as User
from api.securite import decode_access_token

# FastAPI récupère ainsi automatiquement 
# Authorization: Bearer <token>
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),) -> User:
    
    """Vérifie le token puis retourne l'utilisateur correspondant."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Bearer"},)

    try:
        # credentials.credentials contient seulement le JWT,
        # sans le préfixe "Bearer".
        payload = decode_access_token(credentials.credentials)
        username = payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )

    # On recharge l'utilisateur depuis PostgreSQL.
    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inconnu",
        )

    return user


def require_roles(*allowed_roles: str):
    """Crée une dépendance autorisant uniquement certains rôles."""

    def check_role(
        # L'authentification est effectuée avant le contrôle du rôle.
        current_user: User = Depends(get_current_user),
    ) -> User:

        # Ici l'utilisateur est authentifié.
        # Un rôle insuffisant produit donc un 403 et non un 401.
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acces reserve au role exploitant",
            )

        return current_user

    return check_role
