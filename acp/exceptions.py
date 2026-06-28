# -*- coding: utf-8 -*-
"""acp/exceptions.py — ACP istisna sınıfları."""

class ACPError(Exception):
    """ACP temel hata sınıfı."""

class ACPConnectionError(ACPError):
    """ACP bağlantı hatası."""

class ACPAuthError(ACPError):
    """ACP kimlik doğrulama hatası."""

class ACPSessionError(ACPError):
    """ACP oturum hatası."""

class ACPPermissionError(ACPError):
    """ACP izin hatası."""

class ACPTimeoutError(ACPError):
    """ACP zaman aşımı hatası."""

if __name__ == '__main__':
    print('acp.exceptions importlandı.')


class RequestError(ACPError):
    """ACP istek hatası."""
    def __init__(self, message: str = '', status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class ResponseError(ACPError):
    """ACP yanıt hatası."""
