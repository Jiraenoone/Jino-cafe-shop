"""
core/config.py — การตั้งค่าแอพพลิเคชัน

ใช้ Pydantic Settings เพื่ออ่านค่าจาก environment variables (.env)
ทุก secret ต้องมาจาก env vars หรือ Azure Key Vault เท่านั้น
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """การตั้งค่าทั้งหมดของแอพพลิเคชัน อ่านจาก environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────
    app_name: str = "Jino Café API"
    app_env: str = "development"
    debug: bool = False
    allowed_origins: str = "http://localhost:3000"

    # ── Database ─────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./jinocafe_dev.db"

    # ── Azure Service Bus ────────────────────────────────────
    servicebus_namespace: str = ""
    servicebus_queue_name: str = "order-created"
    servicebus_connection_string: str = ""

    # ── Azure Key Vault ──────────────────────────────────────
    key_vault_url: str = ""

    # ── Application Insights ─────────────────────────────────
    applicationinsights_connection_string: str = ""

    # ── Admin Auth ───────────────────────────────────────────
    admin_api_key: str = "dev-admin-key-change-this-in-production"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def allowed_origins_list(self) -> List[str]:
        """แปลง string ที่คั่นด้วย comma เป็น list"""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def use_managed_identity(self) -> bool:
        """ใช้ Managed Identity ถ้าไม่มี connection string"""
        return not self.servicebus_connection_string and bool(self.servicebus_namespace)


@lru_cache
def get_settings() -> Settings:
    """
    Singleton pattern — อ่านค่า settings ครั้งเดียว cache ไว้
    ใช้ @lru_cache เพื่อไม่ให้อ่านไฟล์ .env ซ้ำทุกครั้ง
    """
    return Settings()
