"""FastAPI dependencies for dependency injection."""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status

from src.config import Settings, get_settings


def get_config() -> Settings:
    """Get application settings."""
    return get_settings()


async def verify_api_key(
    x_api_key: Annotated[Optional[str], Header()] = None,
    settings: Settings = Depends(get_config),
) -> Optional[str]:
    """
    Verify API key if authentication is enabled.
    """
    if not settings.api_key_enabled:
        return None

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return x_api_key


# Type aliases for dependency injection
ConfigDep = Annotated[Settings, Depends(get_config)]
ApiKeyDep = Annotated[Optional[str], Depends(verify_api_key)]
