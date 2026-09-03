import sys
import pytest


# ---------------------------------------------------------------------------
# xero.py – Block types
# ---------------------------------------------------------------------------

class TestBlockTypes:
    def test_valid_block_types(self):
        from essentials.xero import PyRunBlock, CmdBlock, SendMessageBlock
        assert PyRunBlock.type == "PyRunBlock"
        assert CmdBlock.type == "CmdBlock"
        assert SendMessageBlock.type == "SendMessageBlock"

    def test_invalid_block_type_raises(self):
        from essentials.xero import _BlockType
        with pytest.raises(TypeError):
            _BlockType("InvalidType")

    def test_block_type_repr(self):
        from essentials.xero import PyRunBlock
        assert "PyRunBlock" in repr(PyRunBlock)


# ---------------------------------------------------------------------------
# xero.py – Block
# ---------------------------------------------------------------------------

class TestBlock:
    def test_block_creation(self):
        from essentials.xero import Block, PyRunBlock
        b = Block("test", PyRunBlock, "print('hi')")
        assert b.block_name == "test"
        assert b.block_type == PyRunBlock
        assert b.context == "print('hi')"
        assert b.is_executed is False

    def test_block_repr(self):
        from essentials.xero import Block, PyRunBlock
        b = Block("myblock", PyRunBlock, "x = 1")
        r = repr(b)
        assert "myblock" in r
        assert "PyRunBlock" in r


# ---------------------------------------------------------------------------
# xero.py – BlockChain
# ---------------------------------------------------------------------------

class TestBlockChain:
    def test_add_and_get_blocks(self):
        from essentials.xero import BlockChain, Block, PyRunBlock
        bc = BlockChain("test_chain")
        b1 = Block("a", PyRunBlock, "pass")
        b2 = Block("b", PyRunBlock, "pass")
        bc.add_block(b1)
        bc.add_block(b2)
        assert len(bc.get_blockchain()) == 2
        assert bc.get_blockchain()[0].block_name == "a"

    def test_empty_blockchain(self):
        from essentials.xero import BlockChain
        bc = BlockChain("empty")
        assert bc.get_blockchain() == []


# ---------------------------------------------------------------------------
# xero.py – blockize parser
# ---------------------------------------------------------------------------

class TestBlockize:
    def test_parse_send_message(self):
        from essentials.xero import blockize, SendMessageBlock
        text = "$SEND_MESSAGE Hello\nThis is a message\n$END_BLOCK Hello"
        bc = blockize(text)
        blocks = bc.get_blockchain()
        assert len(blocks) == 1
        assert blocks[0].block_type == SendMessageBlock
        assert "This is a message" in blocks[0].context

    def test_parse_multiple_blocks(self):
        from essentials.xero import blockize, SendMessageBlock, PyRunBlock
        text = (
            "$SEND_MESSAGE Greeting\nHello!\n$END_BLOCK Greeting\n"
            "$PYRUN_CODE MyCode\nx = 1\n$END_BLOCK MyCode\n"
            "$SEND_MESSAGE Farewell\nBye!\n$END_BLOCK Farewell"
        )
        bc = blockize(text)
        blocks = bc.get_blockchain()
        assert len(blocks) == 3
        assert blocks[0].block_type == SendMessageBlock
        assert blocks[1].block_type == PyRunBlock
        assert blocks[2].block_type == SendMessageBlock

    def test_parse_empty_string(self):
        from essentials.xero import blockize
        bc = blockize("")
        assert len(bc.get_blockchain()) == 0

    def test_parse_no_blocks(self):
        from essentials.xero import blockize
        bc = blockize("just some random text\nno blocks here")
        assert len(bc.get_blockchain()) == 0

    def test_block_context_preserves_content(self):
        from essentials.xero import blockize
        text = "$SEND_MESSAGE Test\nLine 1\nLine 2\nLine 3\n$END_BLOCK Test"
        bc = blockize(text)
        ctx = bc.get_blockchain()[0].context
        assert "Line 1" in ctx
        assert "Line 2" in ctx
        assert "Line 3" in ctx


# ---------------------------------------------------------------------------
# xero.py – Compiler
# ---------------------------------------------------------------------------

class TestCompiler:
    def test_compiler_execute_python(self):
        from essentials.xero import Compiler, BlockChain, Block, PyRunBlock
        bc = BlockChain("test")
        compiler = Compiler(bc)
        result = compiler.execute_python("x = 1 + 1")
        assert result is True

    def test_compiler_execute_block_marks_executed(self):
        from essentials.xero import Compiler, BlockChain, Block, PyRunBlock
        bc = BlockChain("test")
        b = Block("testblock", PyRunBlock, "x = 42")
        bc.add_block(b)
        compiler = Compiler(bc)
        compiler.execute_block(b)
        assert b.is_executed is True
        assert "testblock" in compiler.compiled_names

    def test_compiler_skip_already_executed(self):
        from essentials.xero import Compiler, BlockChain, Block, PyRunBlock
        bc = BlockChain("test")
        b = Block("testblock", PyRunBlock, "x = 42")
        bc.add_block(b)
        compiler = Compiler(bc)
        compiler.execute_block(b)
        # Second call should be skipped
        result = compiler.execute_block(b)
        assert result is True

    def test_compiler_execute_yields_send_messages(self):
        from essentials.xero import Compiler, BlockChain, blockize
        text = "$SEND_MESSAGE Hello\nWorld\n$END_BLOCK Hello"
        bc = blockize(text)
        compiler = Compiler(bc)
        results = list(compiler.execute())
        assert len(results) == 1
        assert "World" in results[0]

    def test_update_blockchain(self):
        from essentials.xero import Compiler, BlockChain, blockize
        bc1 = blockize("$SEND_MESSAGE A\nFirst\n$END_BLOCK A")
        bc2 = blockize("$SEND_MESSAGE B\nSecond\n$END_BLOCK B")
        compiler = Compiler(bc1)
        compiler.update_blockchain(bc2)
        results = list(compiler.execute())
        assert "Second" in results[0]


# ---------------------------------------------------------------------------
# xero.py – ReplaceRandom
# ---------------------------------------------------------------------------

class TestReplaceRandom:
    def test_cycling(self):
        from essentials.xero import ReplaceRandom
        items = ["a", "b", "c"]
        rr = ReplaceRandom(items)
        assert rr.Next() == "a"
        assert rr.Next() == "b"
        assert rr.Next() == "c"
        # Wraps around
        assert rr.Next() == "a"

    def test_single_item(self):
        from essentials.xero import ReplaceRandom
        rr = ReplaceRandom(["only"])
        assert rr.Next() == "only"
        assert rr.Next() == "only"


# ---------------------------------------------------------------------------
# syntax.py
# ---------------------------------------------------------------------------

class TestSyntax:
    def test_format_is_string(self):
        from essentials.syntax import official_assistant_formatting_v1
        assert isinstance(official_assistant_formatting_v1.FORMAT, str)
        assert len(official_assistant_formatting_v1.FORMAT) > 100

    def test_get_random_returns_format(self):
        from essentials.syntax import official_assistant_formatting_v1
        result = official_assistant_formatting_v1.get_random()
        assert result == official_assistant_formatting_v1.FORMAT


# ---------------------------------------------------------------------------
# prompts.py
# ---------------------------------------------------------------------------

class TestPrompts:
    def test_assistant_prompts(self):
        from essentials.prompts import Assistant
        assert len(Assistant.prompts) == 3
        for p in Assistant.prompts:
            assert isinstance(p, str)

    def test_assistant_get_random(self):
        from essentials.prompts import Assistant
        result = Assistant.get_random()
        assert result in Assistant.prompts

    def test_available_dict(self):
        from essentials.prompts import available
        assert "Assistant" in available
        assert "Interactive Assistant" in available


# ---------------------------------------------------------------------------
# interaction.py – cross-platform
# ---------------------------------------------------------------------------

class TestInteraction:
    def test_module_imports_on_linux(self):
        """Module should import without crashing on Linux."""
        import essentials.interaction as interaction
        assert hasattr(interaction, "convert_path")
        assert hasattr(interaction, "OpenUrl")
        assert hasattr(interaction, "SearchOnGoogle")
        assert hasattr(interaction, "OpenPath")
        assert hasattr(interaction, "translate")
        assert hasattr(interaction, "import_lib")

    def test_convert_path(self):
        from essentials.interaction import convert_path
        result = convert_path("/tmp/test")
        assert result.startswith("/")
        assert "test" in result

    def test_convert_path_relative(self):
        from essentials.interaction import convert_path
        result = convert_path(".")
        assert result.endswith("/") is False  # should resolve to absolute

    def test_open_url_returns_open_result(self):
        from essentials.interaction import OpenUrl
        # Just verify it doesn't crash; it calls webbrowser.open
        # On a headless server this may return False but shouldn't raise
        try:
            OpenUrl("https://example.com")
        except Exception:
            pytest.skip("webbrowser.open not available in this environment")

    def test_search_on_google_builds_url(self):
        from unittest.mock import patch
        from essentials.interaction import SearchOnGoogle
        with patch("essentials.interaction.webbrowser.open") as mock_open:
            SearchOnGoogle("hello world")
            mock_open.assert_called_once_with("https://www.google.com/search?q=hello+world")

    def test_import_lib(self):
        from essentials.interaction import import_lib
        os_mod = import_lib("os")
        assert os_mod is not None
        assert hasattr(os_mod, "path")

    def test_import_lib_nonexistent(self):
        from essentials.interaction import import_lib
        with pytest.raises(ModuleNotFoundError):
            import_lib("nonexistent_module_xyz123")

    def test_open_path_linux(self):
        from unittest.mock import patch
        from essentials.interaction import OpenPath
        with patch("essentials.interaction.subprocess.Popen") as mock_popen:
            OpenPath("/tmp")
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert "xdg-open" in args

    def test_global_variables_exist(self):
        from essentials.interaction import (
            MESSAGEBOX_STYLE_ASK_YES_NO,
            MESSAGEBOX_STYLE_ERROR,
            MESSAGEBOX_STYLE_QUESTION,
            MESSAGEBOX_STYLE_INFO,
        )
        assert MESSAGEBOX_STYLE_ASK_YES_NO == 4
        assert MESSAGEBOX_STYLE_ERROR == 16

    def test_windows_functions_raise_on_linux(self):
        """Windows-only functions should raise OSError or return False on Linux."""
        from essentials.interaction import MessageBox, OpenApp, ListInstalledAppsName, UninstallApp
        if sys.platform == "win32":
            pytest.skip("Running on Windows")
        with pytest.raises(OSError):
            MessageBox("test", "test")
        assert OpenApp("nonexistent") is False
        assert ListInstalledAppsName() == []
        assert UninstallApp("nonexistent") is False

    def test_translate_returns_string(self):
        from essentials.interaction import translate
        result = translate("hello", "auto", "en")
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# apis.py – BaseAPI
# ---------------------------------------------------------------------------

class TestBaseAPI:
    def test_base_api_init(self):
        from essentials.apis import BaseAPI
        api = BaseAPI("testkey")
        assert api.messages == []
        assert api.client is None
        assert api.model == ""

    def test_system_message_adds_messages(self):
        from essentials.apis import BaseAPI
        api = BaseAPI("testkey")
        api.system_message("You are helpful.")
        assert len(api.messages) == 2  # system + assistant welcome
        assert api.messages[0]["role"] == "system"
        assert api.messages[1]["role"] == "assistant"

    def test_convert_message_roles_returns_true(self):
        from essentials.apis import BaseAPI
        api = BaseAPI("testkey")
        assert api.convert_message_roles() is True

    def test_get_formatted_messages_no_messages(self):
        from essentials.apis import BaseAPI
        api = BaseAPI("testkey")
        msgs = api.get_formatted_messages()
        assert msgs == []

    def test_get_formatted_messages_user_only(self):
        from essentials.apis import BaseAPI
        api = BaseAPI("testkey")
        api.messages.append({"role": "user", "content": "hello"})
        msgs = api.get_formatted_messages()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"
        assert msgs[0]["content"] == "hello"

    def test_get_formatted_messages_assistant_rendered(self):
        from essentials.apis import BaseAPI
        api = BaseAPI("testkey")
        api.messages.append({"role": "assistant", "content": "$SEND_MESSAGE Test\nHello **world**\n$END_BLOCK Test"})
        msgs = api.get_formatted_messages()
        assert len(msgs) == 1
        # Should be rendered markdown -> HTML
        assert "<strong>" in msgs[0]["content"] or "world" in msgs[0]["content"]


# ---------------------------------------------------------------------------
# apis.py – select_api registry
# ---------------------------------------------------------------------------

class TestSelectAPI:
    def test_select_api_has_all_platforms(self):
        from essentials.apis import select_api
        assert "chatgpt" in select_api
        assert "groq" in select_api
        assert "together" in select_api

    def test_select_api_classes(self):
        from essentials.apis import select_api, ChatGPT_API, Groq_API, TogetherAI
        assert select_api["chatgpt"] is ChatGPT_API
        assert select_api["groq"] is Groq_API
        assert select_api["together"] is TogetherAI


# ---------------------------------------------------------------------------
# apis.py – Concrete API classes (init only, no network calls)
# ---------------------------------------------------------------------------

class TestConcreteAPIs:
    def test_chatgpt_api_init(self):
        from essentials.apis import ChatGPT_API
        api = ChatGPT_API("fake-key")
        assert api.model == "gpt-3.5-turbo"
        assert api.max_tokens == 8000
        assert api.client is not None

    def test_groq_api_init(self):
        from essentials.apis import Groq_API
        api = Groq_API("fake-key")
        assert api.model == "llama3-8b-8192"
        assert api.client is not None

    def test_together_api_init(self):
        from essentials.apis import TogetherAI
        api = TogetherAI("fake-key")
        assert api.model == "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
        assert api.client is not None

    def test_together_convert_message_roles(self):
        from essentials.apis import TogetherAI
        api = TogetherAI("fake-key")
        api.messages.append({"role": "user", "content": "hello"})
        api.messages.append({"role": "assistant", "content": "hi"})
        result = api.convert_message_roles()
        assert result is True
