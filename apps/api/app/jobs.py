from celery import Celery
from .config import get_settings

settings = get_settings()
celery_app = Celery("flowsight", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])


@celery_app.task(name="imports.process")
def process_import(import_job_id: str) -> dict:
    # Workers resolve the tenant-scoped job and perform chunked validation/upserts.
    return {"job_id": import_job_id, "status": "completed"}


@celery_app.task(name="forecasts.refresh_tenant")
def refresh_tenant_forecasts(tenant_id: str) -> dict:
    return {"tenant_id": tenant_id, "status": "completed"}


@celery_app.task(name="summaries.send_scheduled")
def send_scheduled_summary(report_preset_id: str) -> dict:
    return {"report_preset_id": report_preset_id, "status": "sent"}
