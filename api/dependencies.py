from fastapi import Request
from cassandra.cluster import Session

def get_cassandra(request: Request) -> Session:
    """Récupère la session Cassandra partagée depuis l'état de l'application."""

    return request.app.state.cassandra_session