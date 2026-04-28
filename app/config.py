from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    kamis_cert_id: str = ""
    kamis_cert_key: str = ""
    kamis_base_url: str = "http://www.kamis.or.kr/service/price/xml.do"

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