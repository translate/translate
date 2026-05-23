import builtins
import importlib.util
from pathlib import Path


def test_import_without_enchant_uses_noop_fallback(monkeypatch) -> None:
    module_path = Path(__file__).parents[3] / "translate" / "filters" / "spelling.py"
    real_import = builtins.__import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "enchant" or name.startswith("enchant."):
            raise ImportError("blocked enchant import")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    spec = importlib.util.spec_from_file_location(
        "spelling_without_enchant", module_path
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None

    spec.loader.exec_module(module)

    assert module.available is False
    assert module.check("text", "en") == []
    assert module.simple_check("text", "en") == []
