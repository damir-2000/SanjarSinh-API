from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from twilio.rest import Client

from fastapi.security import OAuth2PasswordRequestForm
from services.auth_service.auth_model import Token
from database.models import User
from database.hashing import Hash
from services.auth_service.token import create_access_token
from services.auth_service.auth_model import VerificationRequest


def log_in(request: OAuth2PasswordRequestForm, db: Session):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Email address")

    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")

    access_token = create_access_token(data={"sub": user.username})
    token = Token(
        access_token=access_token,
        token_type="bearer"
    )
    return token


account_sid = "ACe91c5013dd0d466d54868c26c39f138b"
auth_token = "01ec82f5e4995f45d39773b3f6655c85"
verify_sid = "VA597f9afe0a83f33c2174461bd0cc0a53"

client = Client(account_sid, auth_token)


def send_verification_sms(number: str):
    try:
        verification = client.verify.v2.services(verify_sid).verifications.create(
            to=number,
            channel="sms"
        )
        return {"status": verification.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send verification code")


def verify_sms_code(number: str, request: VerificationRequest):
    code = request.code
    try:
        verification_check = client.verify.v2 \
            .services(verify_sid) \
            .verification_checks \
            .create(to=number, code=code)
        return {"status": verification_check.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to verify code")
