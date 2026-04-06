import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.analyze import router

app = FastAPI(
    title="BugPredictor API",
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "BugPredictor API is running",
        "docs": "Go to /docs to use the API"
    }


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="BugPredictor API Docs"
    ).body.decode("utf-8")

    custom_css = """
    <style>
    textarea {
        background-color: white !important;
        color: black !important;
        min-height: 350px !important;
        font-size: 14px !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }

    .swagger-ui .opblock-body textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }

    .swagger-ui {
        font-size: 14px;
    }
    </style>
    """

    html = html.replace("</head>", custom_css + "</head>")
    return HTMLResponse(content=html)
