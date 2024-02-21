import logging
from typing import Any

import uvicorn  # type: ignore[import-untyped]
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.address_routers import allowed_addresses_router as allowed_ip_router
from src.api.address_routers import banned_addresses_router as banned_ip_router
from src.api.addresses_groups_router import allowed_addresses_api_router as allowed_ip_groups_router
from src.api.addresses_groups_router import banned_addresses_api_router as banned_ip_groups_router
from src.api.allowed_networks_router import api_router as allowed_network_router
from src.api.blacklist_router import api_router as blacklist_router
from src.api.history_router import api_router as history_router
from src.api.ping_router import api_router as ping_router
from src.api.whitelist_router import api_router as whitelist_router
from src.core.config import app_settings
from version import get_version

app_configs: dict[str, Any] = dict(
    {
        # Project name configuration (for OPENAPI visualization)
        'title': app_settings.app_title,
        # Rust based JSON serializer
        'default_response_class': ORJSONResponse,
        'version': get_version(),
    }
)

if app_settings.root_path and app_settings.root_path != '/':
    # root path for proxy serving adoptions (https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
    app_configs['root_path'] = app_settings.root_path

# Show OpenAPI interface if allowed
if app_settings.show_openapi:
    # OpenAPI uri
    app_configs['docs_url'] = '/api/openapi'
    # OpenAPI docs address OpenAPI
    app_configs['openapi_url'] = '/api/openapi.json'

app = FastAPI(**app_configs)
app.include_router(banned_ip_router, prefix='/addresses/banned')
app.include_router(banned_ip_groups_router, prefix='/addresses/banned/groups')
app.include_router(allowed_ip_router, prefix='/addresses/allowed')
app.include_router(allowed_ip_groups_router, prefix='/addresses/allowed/groups')
app.include_router(allowed_network_router, prefix='/networks/allowed')
app.include_router(history_router, prefix='/history')
app.include_router(ping_router, prefix='/ping')
app.include_router(blacklist_router, prefix='/download/blacklist')
app.include_router(whitelist_router, prefix='/download/whitelist')

logging.info('Loading blacklist app, version %s', get_version())

if __name__ == '__main__':
    from uvicorn.config import LOGGING_CONFIG

    LOGGING_CONFIG['formatters']['default']['fmt'] = '%(asctime)s %(levelprefix)s %(message)s'
    LOGGING_CONFIG['formatters']['access'][
        'fmt'
    ] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run('main:app', host=app_settings.host, port=app_settings.port, reload=True)
