from fastapi import APIRouter
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "edunexus_secret_key"
ALGORITHM = "HS256"

# request
class GoogleAuth(BaseModel):
    email: str
    google_id: str


@router.post("/google-login")
def google_login(data: GoogleAuth):

    #  simulate user check
    user_email = data.email

   

     # token generate
    token = jwt.encode(
        {"email": user_email, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Google login success",
        "access_token": token
    }