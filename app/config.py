from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    kamis_cert_id: str = ""
    kamis_cert_key: str = ""
    kamis_base_url: str = "http://www.kamis.or.kr/service/price/xml.do"
    admin_secret: str = ""  # /admin/collect 보호용. 비어있으면 인증 생략.
    google_analytics_id: str = ""  # GA4 측정 ID (G-XXXXXXXXXX). 비어있으면 GA 비활성화.
    google_site_verification: str = ""  # Google Search Console HTML 태그 인증 코드
    naver_site_verification: str = ""   # 네이버 서치어드바이저 인증 코드

    @property
    def sqlalchemy_database_url(self) -> str:
        """Railway는 postgres:// 또는 postgresql:// 형식으로 제공 → psycopg3용으로 변환."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()