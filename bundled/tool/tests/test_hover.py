import sys
import os
import unittest
from unittest.mock import MagicMock
from lsprotocol.types import Position

from mocks import MockLanguageServer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.hover import get_hover_info  # noqa: E402
from common.symbols import fill_workspace  # noqa: E402


class TestHover(unittest.TestCase):
    ls = MockLanguageServer(root_path="bundled/tool/tests/fixtures")
    fill_workspace(ls)

    def test_hover(self):
        doc = self.ls.workspace.get_text_document(
            "file://bundled/tool/tests/fixtures/circle.jac"
        )
        pos = Position(line=11, character=7)
        hover = get_hover_info(self.ls, doc, pos)
        self.assertEqual(
            hover.contents.value,
            "(ability) calculate_area\nFunction to calculate the area of a circle.",
        )
