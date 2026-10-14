"""Tests d'intégration de l'API avec TestClient.

Au moins /sante, /auth/login (OK et KO), une route protégée sans jeton
(401), PUT /incidents/{id}/statut avec le rôle direction (403).
"""

from datetime import datetime
from api.models import Incident
from fastapi.testclient import TestClient
from api.main import app
from tests.conftest import entete
import pytest

client = TestClient(app)

def test_sante():
    """Vérifie que le point de terminaison de santé est accessible à tous."""
    response = client.get("/sante")
    assert response.status_code == 200
    assert "statut" in response.json()


@pytest.mark.parametrize(
    "username, password, expected_status",
    [
        ("direction01", "Formation2026!", 200),
        ("exploitant01", "Formation2026!", 200),
        ("direction01", "MauvaisPass!", 401),
        ("utilisateur_inconnu", "Formation2026!", 401),
    ],
)
def test_login(client, username, password, expected_status):
    """Vérifie les connexions nominales et en échec (OK et KO)."""
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"


@pytest.mark.parametrize(
    "fixture_token, expected_status",
    [
        (None, 401),                  # Non authentifié 
        ("token_direction", 403),     # La direction n'a pas le droit 
        ("token_exploitant", 200),    # L'exploitant peut modifier le statut -> 200 OK
    ],
)
def test_modifier_statut_incident_permissions(client, db_session, request, fixture_token, expected_status):
    """Vérifie les restrictions d'accès et les contrôles de rôles (RBAC) sur les incidents."""
    
    # 1. Créer d'abord un incident en base de données pour qu'il existe (ID "1")
    i1 = Incident(
        incident_id="1",
        statut="ouvert",
        cible="velo",
        velo_id="V1",
        type_incident="technique",
        date_signalement=datetime(2026, 8, 24, 10, 0, 0),
    )
    db_session.add(i1)
    db_session.commit()

    # 2. Récupérer le token et appeler l'API
    headers = entete(request.getfixturevalue(fixture_token)) if fixture_token else {}
    
    response = client.put(
        "/incidents/1/statut",
        json={"statut": "resolu"},
        headers=headers
    )
    assert response.status_code == expected_status


    # 2. Récupérer le token et appeler l'API

    headers = entete(request.getfixturevalue(fixture_token)) if fixture_token else {}

    response = client.put(
        "/incidents/1/statut",
        json={"statut": "resolu"},
        headers=headers
    )
    assert response.status_code == expected_status