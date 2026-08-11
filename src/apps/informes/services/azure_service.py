import logging
from datetime import datetime, timedelta, timezone

from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from django.conf import settings

logger = logging.getLogger(__name__)

class AzureBlobService:
    @staticmethod
    def generate_url_sas(blob_name, expira_en_min=10):
        account_name = getattr(settings, 'AZURE_ACCOUNT_NAME', None)
        account_key = getattr(settings, 'AZURE_ACCOUNT_KEY', None)
        container_name = getattr(settings, 'AZURE_CONTAINER_NAME', None)

        if not all([account_name, account_key, container_name]):
            logger.error("Faltan credenciales de Azure en el entorno")
            return None

        try:
            sas_token = generate_blob_sas(
                account_name=account_name,
                account_key=account_key,
                container_name=container_name,
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(minutes=expira_en_min),  # noqa: UP017
            )
            return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error al generar URL SAS para '{blob_name}': {e}")
            return None

    