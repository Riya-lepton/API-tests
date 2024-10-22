import os
from os import environ, path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from lib.guard import guard_middleware
from lib.router import FolderRouter
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

BASE = environ.get("BASE", "/v1")
print("BASE", BASE)
api = FastAPI(
    title="Lepton Maps API",
    version="1.0.0",
    swagger_ui_parameters={
        "url": path.join(BASE, "openapi.json"),
    },
    openapi_prefix=f"{BASE}",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.middleware("http")(guard_middleware)


@api.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    request.state.error_message = str(exc.detail)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    request.state.error_message = str(exc)
    return PlainTextResponse(str(exc), status_code=400)


@api.exception_handler(Exception)
async def catchall_exception_handler(request, exc):
    request.state.error_message = str(exc)
    return PlainTextResponse(str(exc), status_code=400)


folderRouter = FolderRouter("routes").load_routes()

for route in folderRouter.routes:
    method, path = list(route.methods)[0], route.path
    print(method, path)

api.include_router(folderRouter)
api.mount(
    "/static",
    StaticFiles(directory="public"),
    name="static",
)
api.add_middleware(GZipMiddleware)


@api.get("/playground", include_in_schema=False)
async def playground():
    return HTMLResponse(
        """
          <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="Lepton Maps API" />
        <title>Lepton Maps API</title>
      </head>
      <body>
        <script
          id="api-reference"
          data-url="/openapi.json"
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>              
    """
    )


@api.get("/health", include_in_schema=False)
async def health():
    return_message = ""

    deployment_color = os.getenv("DEPLOYMENT_COLOR")

    if deployment_color is None:
        return_message = "Not a colored deployment."
    else:
        return_message = deployment_color

    return {"status": "OK", "deployment_color": return_message}
