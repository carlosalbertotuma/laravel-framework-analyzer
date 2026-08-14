from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import glob

from api.database import engine, Base
from api.routes import proxy, reports

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Laravel Framework Analyser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy.router, prefix="/api", tags=["Proxy"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_latest_report():
    html_files = glob.glob(os.path.join(BASE_DIR, "*.html"))
    if not html_files:
        return "krayin_report.html"
    html_files.sort(key=os.path.getmtime, reverse=True)
    return os.path.basename(html_files[0])

@app.get("/")
@app.get("/index.html")
def root():
    return RedirectResponse(url=f"/{find_latest_report()}")

# Serve static files (the HTML reports)
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")
