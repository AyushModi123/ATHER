import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
load_dotenv()
from db import db, engine
from users import UserLoginSchema, UserSignupSchema
from models.users import UsersModel, Base
import bcrypt
from bson import ObjectId
import os
import uvicorn


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SQL_URL = os.getenv('SQL_URL')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return email


@app.post("/signup")
async def signup(user_data: UserSignupSchema):
    email = user_data.email
    password2 = user_data.password2

    email_found = db.query(UsersModel).filter_by(email = email).first()
    if email_found:
        raise HTTPException(status_code=409, detail="This email already exists in the database")
    else:
        hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
        user = UsersModel(
            email=email,
            password=hashed
        )
        db.add(user)
        db.commit()
        access_token = create_access_token({"sub": email})
        return JSONResponse(content={'message': 'User created successfully', 'token': access_token }, status_code=201)

@app.post("/login")
async def login(user_data: UserLoginSchema):
    email = user_data.email
    password = user_data.password
    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user :   
        password_val = user.password
        if bcrypt.checkpw(password.encode('utf-8'), password_val.encode('utf-8')):
            access_token = create_access_token({"sub": email})
            return JSONResponse(content={'access_token': access_token}, status_code=201)    
    raise HTTPException(status_code=401, detail="Invalid Credentials.")


if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=5000, reload=True)