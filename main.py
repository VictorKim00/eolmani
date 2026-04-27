from fastapi import FastAPI

app = FastAPI(
    title="얼마니 (Eolmani)",
    description="오늘 사과 얼마니? — 공공 데이터 기반 식료품 가격 추적 서비스",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "얼마니에 오신 것을 환영합니다"}


@app.get("/health")
def health():
    return {"status": "ok"}