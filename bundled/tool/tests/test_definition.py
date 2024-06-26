import sys
import os
import unittest
from unittest.mock import MagicMock
from lsprotocol.types import Position

from mocks import MockLanguageServer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lsp_server import definition  # noqa: E402
from common.symbols import fill_workspace  # noqa: E402


class TestDefinition(unittest.TestCase):
    ls = MockLanguageServer(root_path="bundled/tool/tests/fixtures")
    fill_workspace(ls)

    def test_definition(self):
        def_params = MagicMock()
        def_params.position = Position(line=53, character=70)
        def_params.text_document.uri = "file://bundled/tool/tests/fixtures/circle.jac"
        output = definition(self.ls, def_params)
        self.assertEqual(output.range.start.line, 11)
