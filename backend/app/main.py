from fastapi import FastAPI, Request
from app.routes import items
from app.config import settings
from app.utils.logger import log_event
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.models.segment import Segment
from aws_xray_sdk.core.models.subsegment import Subsegment
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Configure AWS X-Ray
xray_recorder.configure(service="MyAppTracing", daemon_address="127.0.0.1:2000", sampling=False)

class XRayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start an X-Ray segment for the request
        segment_name = f"{request.method} {request.url.path}"
        with xray_recorder.in_segment(segment_name) as segment:
            log_event("info", f"Started X-Ray segment for {segment_name}", extra={"trace_id": segment.trace_id, "span_id": segment.id})
            segment.put_http_meta("url", str(request.url))
            segment.put_http_meta("method", request.method)
            segment.put_http_meta("user_agent", request.headers.get("User-Agent", "unknown"))

            # Process the request
            response = await call_next(request)

            # Add response metadata
            segment.put_http_meta("status", response.status_code)

        return response
   
app.add_middleware(XRayMiddleware)
app.include_router(items.router)

@app.get("/")
async def read_root():
    log_event("info", "root endpoint hit")
    return {"message": f"Welcome to {settings.app_name}!"}