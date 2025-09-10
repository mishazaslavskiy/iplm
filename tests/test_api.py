#!/usr/bin/env python3

import pytest

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))          

# Import targets
from src.core_methods import ip_manager
from src import ip_model as ip_module
from src import type_model as type_module
from src import models as process_module
from src.database import db_manager


@pytest.fixture
def reset_mocks(monkeypatch):
    # Ensure execute_query and execute_update are harmless by default
    monkeypatch.setattr(db_manager, "execute_query", lambda q, p=None: [], raising=True)
    monkeypatch.setattr(db_manager, "execute_update", lambda q, p=None: 1, raising=True)
    return monkeypatch


def test_find_builds_query_and_returns_ips(reset_mocks, monkeypatch):
    captured = {"query": None, "params": None}

    def fake_execute_query(query, params=None):
        captured["query"] = query
        captured["params"] = params
        # Return rows shaped like DB output for IP.from_dict
        return [
            {
                "id": 1,
                "name": "IP_A",
                "type_id": 10,
                "process_id": 100,
                "revision": "1.0",
                "status": "alpha",
                "provider": "Prov",
                "ip_components": None,
                "description": "",
                "documentation": "",
                "created_at": None,
                "updated_at": None,
            }
        ]

    monkeypatch.setattr(db_manager, "execute_query", fake_execute_query, raising=True)

    ips = ip_manager.find(type_name="CPU", process_name="SoC_1", status="alpha")

    assert len(ips) == 1
    assert captured["query"] is not None and "SELECT i.* FROM ips i" in captured["query"]
    # Ensure joins applied
    assert "JOIN types t" in captured["query"]
    assert "JOIN processes p" in captured["query"]
    # Ensure params are bound in order
    assert captured["params"] == ("CPU", "SoC_1", "alpha")


def test_find_by_type_tree_includes_descendants(reset_mocks, monkeypatch):
    # Mock Type.find_by_name and Type.find_descendants
    class DummyType:
        def __init__(self, id_):
            self.id = id_

        def find_descendants(self):
            return [DummyType(2), DummyType(3)]

    monkeypatch.setattr(type_module.Type, "find_by_name", staticmethod(lambda n: DummyType(1)), raising=True)

    captured = {"params": None}

    def fake_execute_query(query, params=None):
        captured["params"] = params
        return []

    monkeypatch.setattr(db_manager, "execute_query", fake_execute_query, raising=True)

    ips = ip_manager.find_by_type_tree("Digital", include_descendants=True)
    assert isinstance(ips, list)
    # Should query with IN of 3 ids
    assert captured["params"] == (1, 2, 3)


def test_update_calls_save(reset_mocks, monkeypatch):
    # Prepare a dummy IP instance
    class DummyIP:
        def __init__(self):
            self.name = "IP_X"
            self.status = "alpha"
            self.description = ""

        def save(self):
            # Verify new values were set
            return self.status == "production" and self.description == "updated"

    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(lambda n: DummyIP()), raising=True)

    ok = ip_manager.update("IP_X", status="production", description="updated")
    assert ok is True


def test_release_calls_ip_release(reset_mocks, monkeypatch):
    class DummyIP:
        def __init__(self):
            self.released = False

        def release(self):
            self.released = True
            return True

    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(lambda n: DummyIP()), raising=True)

    assert ip_manager.release("IP_Y") is True


def test_change_schema_calls_recreate(reset_mocks, monkeypatch):
    created = {"dropped": False, "created": False}

    def fake_update(query, params=None):
        if query.strip().startswith("DROP TABLE IF EXISTS"):
            created["dropped"] = True
        return 1

    def fake_create(table_name, schema):
        created["created"] = True

    monkeypatch.setattr(db_manager, "execute_update", fake_update, raising=True)
    monkeypatch.setattr(db_manager, "_create_table", fake_create, raising=True)

    ok = ip_manager.change_schema("ips", {"table_name": "ips", "columns": {"id": "INT PRIMARY KEY"}})
    assert ok is True
    assert created["dropped"] is True
    assert created["created"] is True


def test_pack_collects_related(reset_mocks, monkeypatch):
    class DummyType:
        def to_dict(self):
            return {"name": "CPU"}

    class DummyProcess:
        def to_dict(self):
            return {"name": "Proc"}

    class DummyIP:
        def __init__(self, name):
            self.id = 1
            self.name = name
            self.type_id = 10
            self.process_id = 100
            self.revision = "1.0"
            self.status = "production"
            self.provider = ""
            self.ip_components = []
            self.description = ""
            self.documentation = ""
            self.created_at = None
            self.updated_at = None

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "type_id": self.type_id,
                "process_id": self.process_id,
                "revision": self.revision,
                "status": self.status,
                "provider": self.provider,
                "ip_components": None,
                "description": self.description,
                "documentation": self.documentation,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }

        def get_type(self):
            return DummyType()

        def get_process(self):
            return DummyProcess()

    # Mock ip_manager.find to avoid DB
    monkeypatch.setattr(
        ip_manager, "find", lambda **c: [DummyIP("A"), DummyIP("B")], raising=False
    )

    packed = ip_manager.pack({"status": "production"})
    assert packed["metadata"]["total_ips"] == 2
    assert len(packed["ips"]) == 2
    assert packed["ips"][0]["type"]["name"] == "CPU"
    assert packed["ips"][0]["process"]["name"] == "Proc"


def test_fetch_calls_find_by_name(reset_mocks, monkeypatch):
    marker = {"called": False}

    def fake_fbn(name):
        marker["called"] = True
        return object()

    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(fake_fbn), raising=True)

    obj = ip_manager.fetch("SomeIP")
    assert marker["called"] is True
    assert obj is not None
