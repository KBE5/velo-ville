"""Génère un secret aléatoire pour HS256."""

import secrets

print(secrets.token_hex(32))
