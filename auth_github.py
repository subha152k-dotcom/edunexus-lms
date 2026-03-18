from fastapi import APIRouter
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "edunexus_secret_key"
ALGORITHM = "HS256"

class GithubAuth(BaseModel):
    email: str
    github_id: str


@router.post("/github-login")
def github_login(data: GithubAuth):

    token = jwt.encode(
        {"email": data.email, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Github login success",
        "access_token": token
    }