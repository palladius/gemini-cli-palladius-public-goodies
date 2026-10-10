#!/usr/bin/env python3
import subprocess
from pathlib import Path

def test_validate_spartito_on_example():
    base_dir = Path(__file__).resolve().parent.parent
    script = base_dir / "scripts" / "validate_spartito.py"
    example = base_dir / "examples" / "su-di-noi-pupo.md"

    res = subprocess.run(["python3", str(script), str(example)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "valido al 100%" in res.stdout

if __name__ == "__main__":
    test_validate_spartito_on_example()
    print("All tests passed!")
