import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_ROOT = PROJECT_ROOT / "pyact_cli"

if str(CLI_ROOT) not in sys.path:
    sys.path.insert(0, str(CLI_ROOT))
