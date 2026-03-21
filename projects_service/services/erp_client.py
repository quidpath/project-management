import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class ERPClient:
    """Client for inter-service calls to the main ERP backend."""

    def __init__(self):
        self.base_url = settings.ERP_BACKEND_URL
        self.headers = {
            "X-Service-Key": settings.PROJECTS_SERVICE_SECRET,
            "Content-Type": "application/json",
        }

    def _post(self, path, data, corporate_id=None):
        headers = dict(self.headers)
        if corporate_id:
            headers["X-Corporate-Id"] = str(corporate_id)
        try:
            resp = requests.post(
                f"{self.base_url}{path}",
                json=data,
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"ERPClient POST {path} failed: {e}")
            raise

    def create_invoice(self, invoice_data, corporate_id=None):
        return self._post("/api/internal/invoices/", invoice_data, corporate_id)

    def create_journal_entry(self, journal_data, corporate_id=None):
        return self._post("/api/internal/journal-entries/", journal_data, corporate_id)

    def export_billable_hours(self, hours_data, corporate_id=None):
        return self._post("/api/internal/billable-hours/", hours_data, corporate_id)
