from fastapi import APIRouter
from pydantic import BaseModel
import random
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "edunexus_secret_key"
ALGORITHM = "HS256"

router = APIRouter()

 
otp_store = {}

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str


#  SEND OTP
@router.post("/send-otp")
def send_otp(data: OTPRequest):
    otp = str(random.randint(100000, 999999))

    otp_store[data.email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }

    print("OTP:", otp)  

    return {"message": "OTP sent"}


#  VERIFY OTP
@router.post("/verify-otp")
def verify_otp(data: OTPVerify):
    record = otp_store.get(data.email)

    if not record:
        return {"error": "No OTP found"}

    if record["otp"] != data.otp:
        return {"error": "Invalid OTP"}

    if datetime.utcnow() > record["expires"]:
        return {"error": "OTP expired"}

    #  TOKEN GENERATE
    token = jwt.encode(
        {"email": data.email, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "OTP verified",
        "access_token": token
    }