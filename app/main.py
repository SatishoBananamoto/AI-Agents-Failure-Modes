"""FastAPI entrypoint for ICIF-AES verifier."""

from fastapi import FastAPI

from app.schemas import VerifyRequest, VerifyResponse
from app.session_schemas import SessionVerifyRequest, SessionVerifyResponse
from app.session_verifier import verify_session
from app.verifier import verify


app = FastAPI(title="ICIF-AES Verifier", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/verify", response_model=VerifyResponse)
def verify_endpoint(req: VerifyRequest) -> VerifyResponse:
    return verify(req)


@app.post("/verify-session", response_model=SessionVerifyResponse)
def verify_session_endpoint(req: SessionVerifyRequest) -> SessionVerifyResponse:
    return verify_session(req)
