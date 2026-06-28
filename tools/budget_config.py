# -*- coding: utf-8 -*-
"""tools/budget_config.py — Butce yapilandirma sarmalayicisi.

Kok dizindeki budget_config.py modulunu import eder ve
budget_getir() / kaydet() islemlerini delegasyon yoluyla calistirir.
"""
import os
import json


def run(islem='durum', **kwargs) -> str:
    """Butce islemlerini yonetir.

    Parametreler:
        islem (str): 'durum', 'kaydet' veya 'maliyet'
        harcanan (float): Harcanan miktar (islem=durum icin)
        provider (str): Provider adi (islem=maliyet icin)
        token (int): Token sayisi (islem=maliyet icin)
        veri (dict): Kaydedilecek veri (islem=kaydet icin)

    Returns:
        str: Islem sonucu.
    """
    try:
        from budget_config import BudgetConfig

        if islem == 'durum':
            harcanan = kwargs.get('harcanan', 0.0)
            b = BudgetConfig()
            durum = b.butce_durumu(float(harcanan))
            return (
                f"Butce Durumu:\n"
                f"  Harcanan: ${durum['harcanan']}\n"
                f"  Kalan:    ${durum['kalan']}\n"
                f"  Yuzde:    {durum['yuzde']}%\n"
                f"  Limit:    ${durum['limit']}"
            )

        elif islem == 'kaydet':
            veri = kwargs.get('veri', {})
            dosya_yolu = kwargs.get('dosya_yolu', '')
            if dosya_yolu:
                with open(dosya_yolu, 'w', encoding='utf-8') as f:
                    json.dump(veri, f, ensure_ascii=False, indent=2)
                return f"Butce '{dosya_yolu}' dosyasina kaydedildi."
            return "Hata: 'dosya_yolu' parametresi zorunludur."

        elif islem == 'maliyet':
            provider = kwargs.get('provider', 'deepseek')
            token = int(kwargs.get('token', 0))
            b = BudgetConfig()
            maliyet = b.provider_maliyeti(provider, token)
            return f"{token} token {provider}: ${maliyet:.4f}"

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Butce hatasi: {e}"
