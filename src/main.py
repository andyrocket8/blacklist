from typing import Any

import uvicorn  # type: ignore[import-untyped]
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.allowed_addresses_router import api_router as allowed_ip_router
from src.api.allowed_networks_router import api_router as allowed_network_router
from src.api.banned_addresses_router import api_router as banned_ip_router
from src.core.config import app_settings

app_configs: dict[str, Any] = dict(
    {
        # Project name configuration (for OPENAPI visualization)
        'title': app_settings.app_title,
        # Rust based JSON serializer
        'default_response_class': ORJSONResponse,
    }
)


# Show OpenAPI interface if allowed
if app_settings.show_openapi:
    # OpenAPI uri
    app_configs['docs_url'] = '/api/openapi'
    # OpenAPI docs address OpenAPI
    app_configs['openapi_url'] = '/api/openapi.json'


app = FastAPI(**app_configs)
app.include_router(banned_ip_router, prefix='/addresses/banned')
app.include_router(allowed_ip_router, prefix='/addresses/allowed')
app.include_router(allowed_network_router, prefix='/networks/allowed')


if __name__ == '__main__':
    uvicorn.run('main:app', host=app_settings.host, port=app_settings.port, reload=True)
