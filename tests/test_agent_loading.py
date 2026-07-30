import importlib
import sys
import types
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent_loader import load_agent_components


class AgentLoadingTests(unittest.TestCase):
    def test_returns_fallback_when_import_fails(self):
        def failing_importer(name):
            raise ImportError("missing dependency")

        components, error = load_agent_components(importer=failing_importer)

        self.assertIsNone(components["build_search_agent"])
        self.assertIsNone(components["build_reader_agent"])
        self.assertIsNone(components["writer_chain"])
        self.assertIsNone(components["critic_chain"])
        self.assertIsInstance(error, ImportError)

    def test_returns_components_from_imported_module(self):
        fake_module = types.SimpleNamespace(
            build_search_agent=lambda: "search",
            build_reader_agent=lambda: "reader",
            writer_chain="writer",
            critic_chain="critic",
        )

        def importer(name):
            self.assertEqual(name, "agents")
            return fake_module

        components, error = load_agent_components(importer=importer)

        self.assertEqual(components["build_search_agent"](), "search")
        self.assertEqual(components["build_reader_agent"](), "reader")
        self.assertEqual(components["writer_chain"], "writer")
        self.assertEqual(components["critic_chain"], "critic")
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
