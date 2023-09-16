from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import database
from fastapi.security import OAuth2PasswordRequestForm

from services.auth_service.auth import log_in, send_verification_sms, verify_sms_code
from services.auth_service.auth_model import VerificationRequest

router = APIRouter(
    tags=['Authentication']
)

get_db = database.get_db


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    return log_in(request, session)


@router.post("/send_verification")
def send_verification(number: str):
    return send_verification_sms(number)


@router.post("/verify_code")
def verify_code(number: str, request: VerificationRequest):
    return verify_sms_code(number, request)
