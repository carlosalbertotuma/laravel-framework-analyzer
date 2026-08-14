import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api.models import ReportJob
from api.schemas import ReportRequest, ReportResponse
from api.services.report_service import ReportService

router = APIRouter()

@router.post("/", response_model=ReportResponse)
def generate_report(request: ReportRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Enfileira a geração de um relatório PDF.
    """
    job = ReportService.create_report_job(db, request.campaign_name, len(request.endpoints_data))
    
    # Envia para processamento em background (simula a Fila)
    background_tasks.add_task(ReportService.process_report_job, db, job.id, request.endpoints_data)
    
    return job

@router.get("/", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    """
    Lista histórico de relatórios.
    """
    jobs = db.query(ReportJob).order_by(ReportJob.created_at.desc()).all()
    return jobs

@router.get("/{report_id}", response_model=ReportResponse)
def get_report_status(report_id: str, db: Session = Depends(get_db)):
    """
    Obtém status de um job de relatório pelo report_id.
    """
    job = db.query(ReportJob).filter(ReportJob.report_id == report_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    return job

@router.get("/{report_id}/download")
def download_report(report_id: str, db: Session = Depends(get_db)):
    """
    Baixa o arquivo PDF gerado.
    """
    job = db.query(ReportJob).filter(ReportJob.report_id == report_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
        
    if job.status != "COMPLETED" or not job.file_path:
        raise HTTPException(status_code=400, detail="Relatório ainda não concluído.")
        
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "storage", job.file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo PDF não encontrado no disco.")
        
    return FileResponse(path=file_path, filename=job.file_path, media_type='application/pdf')
