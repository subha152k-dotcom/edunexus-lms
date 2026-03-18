from fastapi import APIRouter
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "edunexus_secret_key"
ALGORITHM = "HS256"

class FacebookAuth(BaseModel):
    email: str
    facebook_id: str


@router.post("/facebook-login")
def facebook_login(data: FacebookAuth):

    token = jwt.encode(
        {"email": data.email, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Facebook login success",
        "access_token": token
    }