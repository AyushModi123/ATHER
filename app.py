import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, Response
from typing import Annotated
import bcrypt
from bson import ObjectId
import os
import uvicorn
import io
from dotenv import load_dotenv
load_dotenv()
from db import db, engine
from schemas import UserLoginSchema, UserSignupSchema
from models.models import Base, UsersModel, EducationModel, ExperienceModel, SkillsModel, UserDetailsModel
from resources.preprocess_prompt import DataExtraction, generate_cold_email, generate_referral_email



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

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

def get_user_details(current_user_id):
    details = db.query(UserDetailsModel).filter_by(id=current_user_id).first()
    experience = db.query(ExperienceModel).filter_by(id=current_user_id).all()
    education = db.query(EducationModel).filter_by(id=current_user_id).all()
    skills = db.query(SkillsModel).filter_by(id=current_user_id).first()
    
    applicant_details = {"details": details.to_dict(), "experience": [exp.to_dict() for exp in experience], "education": [edu.to_dict() for edu in education], "skills": skills.to_dict()}
    return applicant_details

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(UsersModel).filter_by(email=email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_verified_user(current_user: Annotated[UsersModel, Depends(get_current_user)]):
    if not current_user.verify_status:
        raise HTTPException(status_code=400, detail="User is not verified")
    return current_user


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
async def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = user_data.username
    password = user_data.password
    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user :   
        password_val = user.password
        if bcrypt.checkpw(password.encode('utf-8'), password_val.encode('utf-8')):
            access_token = create_access_token({"sub": email})
            return JSONResponse(content={'access_token': access_token, "token_type": "bearer"}, status_code=201)    
    raise HTTPException(status_code=401, detail="Invalid Credentials.")

@app.post("/upload_resume")
async def upload_resume(file: UploadFile, current_user: str = Depends(get_current_verified_user)):
    current_user_id = current_user.id
    if file.content_type != "application/pdf":
        return HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_bytes = await file.read()
    de_obj = DataExtraction(io.BytesIO(file_bytes))
    linkedin_link, github_link, leetcode_link, codechef_link, codeforces_link = de_obj.get_profile_links()
    doc = de_obj.parse_resume()
    print(doc)
    cand_details = doc.details
    user_details = UserDetailsModel(
        user_id=current_user_id,
        name = cand_details.name,
        email = cand_details.email,
        contact = cand_details.contact,
        location = cand_details.location,
        linkedin_link = linkedin_link,
        github_link = github_link,
        leetcode_link = leetcode_link,
        codechef_link = codechef_link,
        codeforces_link = codeforces_link
        )
    db.add(user_details)
    for ed in doc.education:
        education = EducationModel(
            user_id=current_user_id,
            name=ed.name,
            stream=ed.stream,
            score=ed.score,
            location=ed.location,
            graduation_year=ed.graduation_year
        )
        db.add(education)
    for exp in doc.experience:
        experience = ExperienceModel(
            user_id = current_user_id,
            company_name=exp.company_name,
            role=exp.role,
            role_desc=exp.role_desc,
            start_date=exp.start_date,
            end_date=exp.end_date
        )
        db.add(experience)
    skills = SkillsModel(
        user_id=current_user_id,
        skills=doc.skills
        )
    db.add(skills)
    db.commit()
    return JSONResponse(content={'message': "PDF file uploaded and parsed successfully."}, status_code=201)

@app.post("/cold_email")
async def cold_email(job_description: str, current_user: str = Depends(get_current_verified_user)):
    current_user_id = current_user.id
    applicant_details = get_user_details(current_user_id=current_user_id)
    print(applicant_details)
    email = generate_cold_email(applicant_details=applicant_details, job_description=job_description)
    
    return JSONResponse(content={"email": {"subject": email.subject, "body": email.body}}, status_code=201)

@app.post("/referral_email")
async def referral_email(job_title: str, current_user: str = Depends(get_current_verified_user)):
    current_user_id = current_user.id
    applicant_details = get_user_details(current_user_id=current_user_id)
    email = generate_referral_email(applicant_details=applicant_details, job_title=job_title)

    return JSONResponse(content={"email": {"subject": email.subject, "body": email.body}}, status_code=201)

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=5000, reload=True)