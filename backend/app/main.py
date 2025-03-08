from fastapi import FastAPI, Request
from app.routes import items
from app.config import settings
from app.utils.logger import logger
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.models.segment import Segment
from aws_xray_sdk.core.models.subsegment import Subsegment
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Configure AWS X-Ray
xray_recorder.configure(service="MyAppTracing", daemon_address="127.0.0.1:2000")
#patch_all()

# Custom X-Ray Middleware since fastapi isnt natively supported
class XRayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        segment_name = f"{request.method} {request.url.path}"
        with xray_recorder.in_segment(segment_name) as segment:
            segment.put_http_meta("url", str(request.url))
            segment.put_http_meta("method", request.method)
            response = await call_next(request)  # Keep segment open during route execution
            segment.put_http_meta("status", response.status_code)
        return response
   
app.add_middleware(XRayMiddleware)

app.include_router(items.router)

@app.get("/")
async def read_root():
    logger.info("root endpoint hit")
    return {"message": f"Welcome to {settings.app_name}!"}