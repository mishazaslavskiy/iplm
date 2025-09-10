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
                "parent_ip_id": None,
                "revision": "1.0",
                "status": "alpha",
                "provider": "Prov",
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
            self.parent_ip_id = None
            self.revision = "1.0"
            self.status = "production"
            self.provider = ""
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
                "parent_ip_id": self.parent_ip_id,
                "revision": self.revision,
                "status": self.status,
                "provider": self.provider,
                "description": self.description,
                "documentation": self.documentation,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }

        def get_type(self):
            return DummyType()

        def get_process(self):
            return DummyProcess()
        
        def get_parent(self):
            return None
        
        def get_children(self):
            return []

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


def test_add_child_ip_calls_add_child(reset_mocks, monkeypatch):
    class DummyParentIP:
        def add_child(self, child):
            self.child_added = True
            return True

    class DummyChildIP:
        def __init__(self):
            self.name = "ChildIP"

    parent = DummyParentIP()
    child = DummyChildIP()

    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(lambda n: parent if n == "ParentIP" else child), raising=True)

    result = ip_manager.add_child_ip("ParentIP", child)
    assert result is True
    assert parent.child_added is True


def test_remove_child_ip_calls_remove_child(reset_mocks, monkeypatch):
    class DummyParentIP:
        def remove_child(self, child):
            self.child_removed = True
            return True

    class DummyChildIP:
        def __init__(self):
            self.name = "ChildIP"

    parent = DummyParentIP()
    child = DummyChildIP()

    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(lambda n: parent if n == "ParentIP" else child), raising=True)

    result = ip_manager.remove_child_ip("ParentIP", "ChildIP")
    assert result is True
    assert parent.child_removed is True


def test_get_ip_hierarchy_builds_tree(reset_mocks, monkeypatch):
    class DummyType:
        def __init__(self, name):
            self.name = name

    class DummyChildIP:
        def __init__(self, name, id_):
            self.id = id_
            self.name = name
            self.type = DummyType("CPU")
            self.status = "production"

        def get_type(self):
            return self.type

        def get_children(self):
            return []  # No children to avoid recursion

    class DummyIP:
        def __init__(self, name, id_=1):
            self.id = id_
            self.name = name
            self.type = DummyType("CPU")
            self.status = "production"

        def get_type(self):
            return self.type

        def get_children(self):
            return [DummyChildIP("Child1", 2), DummyChildIP("Child2", 3)]

    dummy_ip = DummyIP("ParentIP")
    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(lambda n: dummy_ip), raising=True)

    hierarchy = ip_manager.get_ip_hierarchy("ParentIP")
    assert hierarchy["name"] == "ParentIP"
    assert hierarchy["type"] == "CPU"
    assert hierarchy["status"] == "production"
    assert len(hierarchy["children"]) == 2
    assert hierarchy["children"][0]["name"] == "Child1"
    assert hierarchy["children"][1]["name"] == "Child2"


def test_show_ip_tree_calls_print_tree(reset_mocks, monkeypatch, capsys):
    class DummyType:
        def __init__(self, name):
            self.name = name

    class DummyIP:
        def __init__(self, name, id_=1):
            self.id = id_
            self.name = name
            self.type = DummyType("CPU")
            self.status = "production"
            self.provider = "TestProvider"
            self.revision = "1.0"
            self.description = "Test IP"

        def get_type(self):
            return self.type

        def get_children(self):
            return []

    dummy_ip = DummyIP("TestIP")
    monkeypatch.setattr(ip_module.IP, "find_by_name", staticmethod(lambda n: dummy_ip), raising=True)

    ip_manager.show_ip_tree("TestIP")
    captured = capsys.readouterr()
    assert "IP Tree for 'TestIP':" in captured.out
    assert "├─ TestIP (CPU) - production" in captured.out


def test_show_ip_tree_all_roots(reset_mocks, monkeypatch, capsys):
    class DummyType:
        def __init__(self, name):
            self.name = name

    class DummyIP:
        def __init__(self, name, id_=1):
            self.id = id_
            self.name = name
            self.type = DummyType("CPU")
            self.status = "production"

        def get_type(self):
            return self.type

        def get_children(self):
            return []

    dummy_ips = [DummyIP("Root1"), DummyIP("Root2")]
    monkeypatch.setattr(ip_module.IP, "find_roots", staticmethod(lambda: dummy_ips), raising=True)

    ip_manager.show_ip_tree()
    captured = capsys.readouterr()
    assert "All IP Trees:" in captured.out
    assert "├─ Root1 (CPU) - production" in captured.out
    assert "├─ Root2 (CPU) - production" in captured.out
