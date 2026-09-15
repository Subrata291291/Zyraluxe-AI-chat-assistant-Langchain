from fastapi.middleware.cors import CORSMiddleware
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

API_FILE = (
    PROJECT_ROOT
    / "product"
    / "77_product_search_api.py"
)


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


api_module = load_module(
    "product_search_api",
    API_FILE
)


app = api_module.app


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health_check():
    return {
        "success": True,
        "service": "Zyra Luxe Product API",
        "status": "healthy"
    }