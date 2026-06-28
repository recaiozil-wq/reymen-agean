"""
Modal yardımcı araçları.

Modal ile ilgili ortak yardımcı fonksiyonlar.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def modal_mevcut() -> bool:
    """Modal kütüphanesinin yüklü olup olmadığını kontrol eder."""
    try:
        import modal  # noqa: F401
        return True
    except ImportError:
        return False


def modal_versiyon() -> Optional[str]:
    """Modal kütüphane versiyonunu döndürür."""
    try:
        import modal
        return getattr(modal, "__version__", "bilinmiyor")
    except ImportError:
        return None


def token_kontrol() -> dict[str, Any]:
    """Modal token'larının durumunu kontrol eder.

    Returns:
        Token durum bilgisi.
    """
    token_id = os.environ.get("MODAL_TOKEN_ID")
    token_secret = os.environ.get("MODAL_TOKEN_SECRET")

    if token_id and token_secret:
        return {
            "token_id": token_id[:8] + "..." if len(token_id) > 8 else token_id,
            "token_secret": "***" + token_secret[-4:] if token_secret else "yok",
            "durum": "hazir",
        }
    return {
        "token_id": token_id[:8] + "..." if token_id else "yok",
        "token_secret": "***" + token_secret[-4:] if token_secret else "yok",
        "durum": "token_eksik",
        "mesaj": "MODAL_TOKEN_ID ve MODAL_TOKEN_SECRET ortam değişkenlerini ayarlayın",
    }


def basit_fonksiyon(fn, **modal_kwargs):
    """Bir fonksiyonu Modal'a dağıtılabilir hale getirir.

    Args:
        fn: Dekore edilecek fonksiyon.
        **modal_kwargs: Modal @app.function() parametreleri.

    Returns:
        Modal dağıtılabilir fonksiyon.
    """
    if not modal_mevcut():
        logger.warning("Modal mevcut değil, fonksiyon olduğu gibi döndürülüyor")
        return fn

    import modal

    app = modal.App("ReYMeN-utils")

    @app.function(**modal_kwargs)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def run(**kwargs) -> str:
    """Modal ortamını test eder."""
    import json

    modal_var = modal_mevcut()
    versiyon = modal_versiyon()
    token_durum = token_kontrol()

    return json.dumps({
        "modal_mevcut": modal_var,
        "versiyon": versiyon,
        "token_durum": token_durum,
    }, indent=2, ensure_ascii=False)
