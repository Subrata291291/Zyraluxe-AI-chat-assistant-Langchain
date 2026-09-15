import importlib.util
from pathlib import Path

file_path = Path(__file__).parent / "product" / "91_unified_chat_response.py"

spec = importlib.util.spec_from_file_location("unified_chat_response", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app