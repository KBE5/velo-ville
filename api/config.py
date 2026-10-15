"""Chargement des paramètres depuis .env."""

import os
from dotenv import load_dotenv

# Charge les variables du fichier .env.
load_dotenv()

# connexion PostgreSQL
DATABASE_URL = os.environ["DATABASE_URL"]
DATABASE_URL_TEST = os.environ["DATABASE_URL_TEST"]

# Params pour signer et vérifier les JWT
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10"))



# Paramètres utilisés pour le front 
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_TIMEOUT_SECONDES = int(os.getenv("API_TIMEOUT_SECONDES", 15))