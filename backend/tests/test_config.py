from app.core.config import settings

def test_settings_load_defaults() -> None:
    assert settings.APP_NAME == "AxonTime HR"
    assert settings.API_V1_STR == "/api/v1"
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) >= 1
