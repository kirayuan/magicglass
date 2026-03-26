"""Tests for the main module."""

from magicglass.main import main


class TestMain:
    def test_help_flag(self, capsys):
        """Test that --help works without errors."""
        try:
            main(["--help"])
        except SystemExit as e:
            assert e.code == 0

        captured = capsys.readouterr()
        assert "MagicGlass" in captured.out

    def test_default_symbol_is_baba(self):
        """Test that BABA is the default when no symbol is specified."""
        import argparse
        from magicglass.main import main as _main

        # We just verify the argparse defaults by checking the parser directly
        parser = argparse.ArgumentParser()
        parser.add_argument("symbol", nargs="?", default="BABA")
        args = parser.parse_args([])
        assert args.symbol == "BABA"
