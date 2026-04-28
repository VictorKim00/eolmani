from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    kamis_cert_id: str = ""
    kamis_cert_key: str = ""
    kamis_base_url: str = "http://www.kamis.or.kr/service/price/xml.do"


settings = Settings()