from dataclasses import dataclass
import json
from typing import Any


@dataclass
class OculusQuery:
    """
    Dataclass holding representation of GraphQL query

    Meta generally does not use raw GraphQL queries over the network,
    instead, designated queries are assigned document IDs, and callers
    can substitute variables into these documents to create custom queries.
    """

    doc_id: str | None = None
    doc: str | None = None
    variables: dict[Any, Any] | None = None

    def encode(self, access_token: str) -> str:
        return f"access_token={access_token}&variables={json.dumps(self.variables or {})}&doc_id={self.doc_id or ''}&doc={self.doc or ''}"

    def make_uri(self, base_uri: str, access_token: str) -> str:
        return f"{base_uri}?{self.encode(access_token)}"
