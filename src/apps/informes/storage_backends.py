import logging

from django.conf import settings
from storages.backends.azure_storage import AzureStorage

logger = logging.getLogger(__name__)

class AzureMediaStorage(AzureStorage):
    # Backend para el alta de archivos (Images) para el almacenamiento en Azure Storage
    account_name = getattr(settings, 'AZURE_ACCOUNT_NAME', None)
    account_key = getattr(settings, 'AZURE_ACCOUNT_KEY', None)
    azure_container = getattr(settings, 'AZURE_CONTAINER_NAME', None)

    expiration_secs = None

    def _save(self, name, content):
        logger.info(f"[Informes] Intentando subir archivo a Azure Storage: {name}")

        try:
            result = super()._save(name, content)
            logger.info(f"[Informes] archivo '{name}' subido exitosamente a Azure Storage.")
            return result
        
        except Exception as e:
            logger.error(f"[Informes] Error al subir archivo '{name}' a Azure Storage: {str(e)}")  # noqa: RUF010
            raise e  # noqa: TRY201

