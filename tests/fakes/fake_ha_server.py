# -*- coding: utf-8 -*-
"""tests/fakes/fake_ha_server.py — Sahte Home Assistant sunucusu."""


class FakeHAServer:
    """Home Assistant API sahte sunucusu."""

    def __init__(self, host: str = "localhost", port: int = 8123):
        self.host = host
        self.port = port
        self._states: dict = {}
        self._services: dict = {}
        self.requests: list = []

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def add_state(self, entity_id: str, state: str, attributes: dict = None) -> None:
        self._states[entity_id] = {
            "entity_id": entity_id,
            "state": state,
            "attributes": attributes or {},
        }

    def get_state(self, entity_id: str) -> dict:
        return self._states.get(entity_id, {})

    def handle_request(self, method: str, path: str, data: dict = None) -> dict:
        self.requests.append({"method": method, "path": path, "data": data})
        if path.startswith("/api/states/"):
            entity_id = path.split("/")[-1]
            return self._states.get(entity_id, {})
        return {"status": "ok"}


if __name__ == "__main__":
    server = FakeHAServer()
    server.add_state("light.living_room", "on")
    print("FakeHAServer importlandı:", server.base_url)

ENTITY_STATES = {"on": "on", "off": "off", "unavailable": "unavailable"}
