import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from app.routes.analyze import router

app = FastAPI(
    title="BugPredictor API",
    docs_url=None,     # ❌ disable default docs
    redoc_url=None     # optional
)

# ✅ Include routes
app.include_router(router)


# ✅ ROOT ROUTE (Homepage)
@app.get("/")
def home():
    return {
        "message": "🚀 BugPredictor API is running",
        "docs": "Go to /docs to use the API"
    }


# ✅ CUSTOM SWAGGER UI (Styled)
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="BugPredictor API Docs"
    ).body.decode("utf-8")

    # 🔥 CUSTOM CSS
    custom_css = """
    <style>
    
    /* 🔥 Make input box BIG + WHITE */
    textarea {
        background-color: white !important;
        color: black !important;
        min-height: 350px !important;
        font-size: 14px !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }

    /* Target Swagger specific textarea */
    .swagger-ui .opblock-body textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }

    /* Improve overall readability */
    .swagger-ui {
        font-size: 14px;
    }

    </style>
    """

    html = html.replace("</head>", custom_css + "</head>")
    return HTMLResponse(content=html)