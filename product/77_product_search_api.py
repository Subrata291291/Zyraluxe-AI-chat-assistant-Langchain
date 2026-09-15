from fastapi import FastAPI
from pydantic import BaseModel
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

API_RESPONSE_FILE = (
    PROJECT_ROOT
    / "product"
    / "76_api_product_response.py"
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
    "api_product_response",
    API_RESPONSE_FILE
)


app = FastAPI(
    title="Zyra Luxe AI Product API",
    version="1.0.0"
)


class ProductSearchRequest(BaseModel):
    query: str


service = api_module.APIProductResponse()


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Zyra Luxe Product API is running"
    }


@app.post("/products/search")
def search_products(request: ProductSearchRequest):

    return service.create_response(
        request.query
    )