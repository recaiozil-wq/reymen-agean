"""
Notion MCP Entegrasyonu — ReYMeN Cron Job Sonuçlarını Notion'a Yazma.

Cron job tamamlandığında sonucu otomatik olarak bir Notion veritabanına kaydeder.
Notion API token ve veritabanı ID'si .env dosyasından okunur.

Gerekli .env değişkenleri:
  NOTION_API_TOKEN=secret_xxxxx
  NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# ── Constants ───────────────────────────────────────────────────────
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionWriter:
    """Write cron job results to a Notion database."""

    def __init__(
        self,
        token: Optional[str] = None,
        database_id: Optional[str] = None,
    ):
        self.token = token or os.getenv("NOTION_API_TOKEN", "")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID", "")

        if not self.token:
            logger.warning(
                "NOTION_API_TOKEN bulunamadı. Notion yazmaları devre dışı."
            )
        if not self.database_id:
            logger.warning(
                "NOTION_DATABASE_ID bulunamadı. Notion yazmaları devre dışı."
            )

        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }

    @property
    def is_configured(self) -> bool:
        """Check if the writer has valid credentials."""
        return bool(self.token and self.database_id)

    def write_job_result(
        self,
        job_name: str,
        status: str,
        command: str,
        exit_code: Optional[int] = None,
        log_summary: str = "",
        duration_seconds: Optional[float] = None,
        extra_properties: Optional[dict] = None,
    ) -> dict:
        """
        Write a cron job result to the Notion database.

        Args:
            job_name: Name of the cron job
            status: 'success', 'failed', or 'running'
            command: The shell command that was executed
            exit_code: Process exit code
            log_summary: Short log preview / summary
            duration_seconds: How long the job took
            extra_properties: Additional Notion property overrides

        Returns:
            Notion API response dict, or error dict
        """
        if not self.is_configured:
            return {"error": "Notion yapılandırması eksik. NOTION_API_TOKEN ve NOTION_DATABASE_ID kontrol edin."}

        url = f"{NOTION_API_BASE}/pages"

        # Build properties
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {"content": job_name}
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": self._map_status(status),
                }
            },
            "Command": {
                "rich_text": [
                    {
                        "text": {"content": command[:2000]},
                    }
                ]
            },
            "Timestamp": {
                "date": {
                    "start": datetime.now(timezone.utc).isoformat(),
                }
            },
        }

        # Add optional fields
        if exit_code is not None:
            properties["Exit Code"] = {
                "number": exit_code
            }

        if log_summary:
            properties["Log Summary"] = {
                "rich_text": [
                    {
                        "text": {"content": log_summary[:2000]},
                    }
                ]
            }

        if duration_seconds is not None:
            properties["Duration (s)"] = {
                "number": round(duration_seconds, 2)
            }

        # Merge extra properties
        if extra_properties:
            properties.update(extra_properties)

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
        }

        try:
            response = requests.post(url, headers=self._headers, json=payload)
            response.raise_for_status()
            data = response.json()
            page_url = data.get("url", "")
            logger.info(
                f"✅ Notion sayfası oluşturuldu: {job_name} -> {page_url}"
            )
            return {
                "success": True,
                "page_id": data.get("id"),
                "page_url": page_url,
                "data": data,
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Notion API hatası: {e}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" | Detay: {error_detail}"
                except (ValueError, KeyError):
                    error_msg += f" | HTTP {e.response.status_code}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Beklenmeyen hata: {e}"
            logger.error(error_msg)
            return {"error": error_msg}

    def write_job_completed(
        self,
        job_name: str,
        command: str,
        status: str,
        exit_code: int,
        output: str,
        duration: float,
    ) -> dict:
        """
        Convenience method: write a completed job result.

        This creates both the main page and a log preview.
        """
        log_preview = output[:500] if output else ""
        if len(output) > 500:
            log_preview += "\n... (log truncated)"

        return self.write_job_result(
            job_name=job_name,
            status=status,
            command=command,
            exit_code=exit_code,
            log_summary=log_preview,
            duration_seconds=duration,
        )

    def verify_connection(self) -> bool:
        """
        Test the Notion API connection by querying the database.
        Returns True if connection is successful.
        """
        if not self.is_configured:
            logger.error("Notion yapılandırması eksik.")
            return False

        url = f"{NOTION_API_BASE}/databases/{self.database_id}"
        try:
            response = requests.get(url, headers=self._headers)
            response.raise_for_status()
            db_info = response.json()
            logger.info(
                f"✅ Notion bağlantısı başarılı: {db_info.get('title', [{}])[0].get('plain_text', 'Unknown')}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Notion bağlantı hatası: {e}")
            return False

    @staticmethod
    def _map_status(status: str) -> str:
        """Map internal status to Notion select option names."""
        mapping = {
            "success": "✅ Success",
            "failed": "❌ Failed",
            "running": "🔄 Running",
            "pending": "⏳ Pending",
            "cancelled": "⛔ Cancelled",
        }
        return mapping.get(status.lower(), status)

    @staticmethod
    def create_database_schema() -> dict:
        """
        Return the recommended Notion database schema for job results.
        Use this to create the database manually via Notion API or UI.
        """
        return {
            "Name": {"title": {}},
            "Status": {"select": {"options": [
                {"name": "✅ Success", "color": "green"},
                {"name": "❌ Failed", "color": "red"},
                {"name": "🔄 Running", "color": "blue"},
                {"name": "⏳ Pending", "color": "gray"},
                {"name": "⛔ Cancelled", "color": "orange"},
            ]}},
            "Command": {"rich_text": {}},
            "Exit Code": {"number": {}},
            "Log Summary": {"rich_text": {}},
            "Duration (s)": {"number": {}},
            "Timestamp": {"date": {}},
        }


# ── CLI Usage ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Notion MCP — Cron job sonuçlarını Notion'a yaz"
    )
    parser.add_argument("--job-name", required=True, help="Job adı")
    parser.add_argument("--status", required=True, help="Job durumu (success/failed)")
    parser.add_argument("--command", default="", help="Çalıştırılan komut")
    parser.add_argument("--exit-code", type=int, default=None, help="Çıkış kodu")
    parser.add_argument("--log", default="", help="Log çıktısı / özeti")
    parser.add_argument("--duration", type=float, default=None, help="Süre (saniye)")
    parser.add_argument("--verify", action="store_true", help="Sadece bağlantıyı test et")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    writer = NotionWriter()

    if args.verify:
        success = writer.verify_connection()
        print(f"Bağlantı durumu: {'✅ Başarılı' if success else '❌ Başarısız'}")
    else:
        result = writer.write_job_result(
            job_name=args.job_name,
            status=args.status,
            command=args.command,
            exit_code=args.exit_code,
            log_summary=args.log,
            duration_seconds=args.duration,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
