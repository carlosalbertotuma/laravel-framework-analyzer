import os
import uuid
import traceback
from datetime import datetime
from sqlalchemy.orm import Session
from api.models import ReportJob
from api.services.report_data_service import ReportDataService
from api.services.pdf_generator import PDFGenerator

class ReportService:
    @staticmethod
    def create_report_job(db: Session, campaign_name: str, total_records: int) -> ReportJob:
        report_id = f"RPT-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}"
        job = ReportJob(
            report_id=report_id,
            campaign_name=campaign_name,
            total_records=total_records,
            status="PENDING",
            progress=0
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def process_report_job(db: Session, job_id: int, endpoints_data: list):
        job = db.query(ReportJob).filter(ReportJob.id == job_id).first()
        if not job:
            return
            
        try:
            job.status = "PROCESSING"
            job.progress = 10
            db.commit()
            
            # Passo 1: Calcular Estatísticas (Progress -> 40%)
            stats = ReportDataService.process_endpoints(endpoints_data)
            
            job.progress = 40
            db.commit()
            
            # Passo 2: Preparar Variáveis de Contexto (Progress -> 60%)
            context = {
                "report_id": job.report_id,
                "campaign_name": job.campaign_name,
                "generated_at": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "stats": stats
            }
            
            job.progress = 60
            db.commit()
            
            # Passo 3: Gerar PDF (Progress -> 90%)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            storage_dir = os.path.join(base_dir, "storage")
            if not os.path.exists(storage_dir):
                os.makedirs(storage_dir)
                
            safe_campaign = "".join(c if c.isalnum() else "_" for c in job.campaign_name)
            filename = f"disparos_{safe_campaign}_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M')}.pdf"
            file_path = os.path.join(storage_dir, filename)
            
            PDFGenerator.generate("report_template.html", context, file_path)
            
            # Passo 4: Concluir (Progress -> 100%)
            job.status = "COMPLETED"
            job.progress = 100
            job.completed_at = datetime.utcnow()
            job.file_path = filename
            db.commit()
            
        except Exception as e:
            db.rollback()
            job = db.query(ReportJob).filter(ReportJob.id == job_id).first()
            if job:
                job.status = "FAILED"
                job.error_message = traceback.format_exc()
                db.commit()
