"""redact shim — testler icin PII temizleme fonksiyonlari."""

import re


def email_temizle(metin):
    return re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", metin)


def telefon_temizle(metin):
    return re.sub(r"\b\d{10}\b", "[TELEFON]", metin)


def kart_temizle(metin):
    metin = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[KART_NO]", metin)
    return metin


def api_key_temizle(metin):
    return re.sub(r"(?i)(api[_-]?key\s*=\s*)\S+", r"\1[GIZLI]", metin)


def tc_temizle(metin):
    return re.sub(r"\b[1-9]\d{10}\b", "[TC_KIMLIK]", metin)


def tam_temizle(metin):
    metin = email_temizle(metin)
    metin = telefon_temizle(metin)
    metin = kart_temizle(metin)
    metin = api_key_temizle(metin)
    metin = tc_temizle(metin)
    return metin
