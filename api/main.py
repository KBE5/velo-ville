"""Point d'entrée de l'API VéloVille (FastAPI).

À compléter : créer l'application, inclure les routeurs (auth, stations, trajets,
incidents, indicateurs) et exposer GET /sante -> {"statut": "ok"}.

Lancement : uvicorn api.main:app --reload
"""

from fastapi import FastAPI
from api.routers import trajets, stations, indicateurs, incidents, auth

app = FastAPI(
    title="VéloVille API",
    description="API de gestion et d'indicateurs du réseau VéloVille",
    version="0.1.0",
)


app.include_router(auth.router)
app.include_router(stations.router)
app.include_router(trajets.router)
app.include_router(incidents.router)
app.include_router(indicateurs.router)



@app.get("/sante", tags=["Santé"])
def verifier_sante():
    
    return {"statut": "ok"}
