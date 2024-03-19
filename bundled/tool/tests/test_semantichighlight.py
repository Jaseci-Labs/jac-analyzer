import sys
import os
import unittest
from unittest.mock import MagicMock

from mocks import MockLanguageServer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lsp_server import semantic_tokens_full   # noqa: E402
from common.symbols import fill_workspace  # noqa: E402


class TestValidate(unittest.TestCase):
    ls = MockLanguageServer("bundled/tool/tests/fixtures")
    fill_workspace(ls)

    def test_semantic_tokens_full(self):
        mock_params = MagicMock()
        mock_params.text_document.uri = (
            "file://bundled/tool/tests/fixtures/circle.jac"
        )
        semantic_tokens = semantic_tokens_full(self.ls, mock_params)
        self.assertIsNotNone(semantic_tokens)
        self.assertEqual(len(semantic_tokens.data), 220)
        # self.assertIn('[5]', semantic_tokens.data)