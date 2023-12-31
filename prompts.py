from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from typing import Optional, Sequence
from pydantic import BaseModel, Field

class CandidateDetailsSchema(BaseModel):
    name: str = Field(None, description="name of person")
    email: str = Field(None, description="email of person")
    contact: str = Field(None, description="contact number of person")
    location: str = Field(None, description="location of person")

class EducationSchema(BaseModel):
    name: str = Field(None, description="name of college or school")
    stream: str = Field(None, description="stream of education")
    score: int = Field(None, description="contains score in this institute")
    location: str = Field(None, description="Location of institute")
    graduation_year: int = Field(None, description="Graduation Year")

class ExperienceSchema(BaseModel):
    company_name: str = Field(None, description="name of company")
    role: str = Field(None, description="role of experience")
    role_desc: str = Field(None, description="max 250 words short description of role")
    start_date: str = Field(None, description="start month and year of experience e.g. 03/2020")
    end_date: str = Field(None, description="end month and year of experience e.g. 06/2020")

class ResumeSchema(BaseModel):
    """Parsing Resume"""
    details: CandidateDetailsSchema = Field(..., description="Contains details of person as dictionary")
    education: Sequence[EducationSchema] = Field(..., description="Contains list of different educations")
    experience: Sequence[ExperienceSchema] = Field(..., description="Contains list of different experiences")
    skills: str = Field(None, description="Contains technical and non technical skills separated by comma")

class EmailSchema(BaseModel):
    """Generate Email"""
    subject: str = Field(..., description="Generate a short precise subject of email")
    body: str = Field(..., description="Generate body of email describing details of resume and how they fit the job")

class CoverLetterSchema(BaseModel):
    """Generate Cover Email"""    
    body: str = Field(..., description="Generate cover letter describing applicant details.")

parse_resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template='''You are a world class algorithm for extracting information in structured formats. Use the given format to extract information from the following input: {resume_text}. 
          Tip: Make sure to answer in the correct format. Return value of fields as None if value not found.'''
)

cold_email_prompt = PromptTemplate(
    input_variables=["applicant_details", "job_description", "website_data"],
    template='''You are a world class algorithm for generating emails in structured formats. Use the given format to write cold email from the following input applicant details: {applicant_details}. JOB DESCRIPTION: {job_description}. COMPANY DETAILS: {website_data}. 
          Tip: Make sure to answer in the correct format. Include relevant applicant details in email. Keep email short and on-point which explains how applicant goals align with company's vision which makes applicant best fit for the role.'''
)

referral_email_prompt = PromptTemplate(
    input_variables=["applicant_details", "job_role"],
    template='''You are a world class algorithm for generating emails in structured formats. Use the given format to write referral email from the following input applicant details: {applicant_details}.
          Tip: Make sure to answer in the correct format. Applicant is asking for referral for this job role: {job_role} from company's employee. Include relevant applicant details in email. Keep email short and on-point.
          Through words, applicant tries to show how much this job can impact the career. Also include 2 line poem in email in professional and funny tone.'''
)

cover_letter_prompt = PromptTemplate(
    input_variables=["applicant_details", "job_description"],
    template='''You are a world class algorithm for generating cover letters for resume in structured formats. Use the given format to write cover letter from the following input applicant details: {applicant_details}. JOB DESCRIPTION: {job_description}. 
          Tip: Make sure to answer in the correct format. Include relevant applicant details in body. Cover letter should include applicant's experience, education and skills. Text in cover letter should describe whole resume(applicant details) in words.'''
)