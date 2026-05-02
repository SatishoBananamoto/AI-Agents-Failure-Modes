"""FastAPI entrypoint for ICIF-AES verifier."""

from fastapi import FastAPI

from app.schemas import VerifyRequest, VerifyResponse
from app.verifier import verify


app = FastAPI(title="ICIF-AES Verifier", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/verify", response_model=VerifyResponse)
def verify_endpoint(req: VerifyRequest) -> VerifyResponse:
    return verify(req)
