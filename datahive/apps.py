from django.apps import AppConfig


class DatahiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datahive'

    def ready(self):
        # Import enhanced models at app ready time to ensure they're registered once
        try:
            from . import model_enhanced  # noqa: F401
        except ImportError as e:
            # If import fails here, let it surface during management commands where appropriate
            import logging
            logging.getLogger(__name__).warning(f"Failed to import model_enhanced: {e}")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Unexpected error importing model_enhanced: {e}")
