from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from typing import Optional, Sequence
from pydantic import BaseModel, Field

class Candidate_Details(BaseModel):
    name: str = Field(None, description="name of person")
    email: str = Field(None, description="email of person")
    contact: str = Field(None, description="contact number of person")
    location: str = Field(None, description="location of person")

class Education(BaseModel):
    name: str = Field(None, description="name of college or school")
    stream: str = Field(None, description="stream of education")
    score: int = Field(None, description="contains score in this institute")
    location: str = Field(None, description="Location of institute")
    graduation_year: int = Field(None, description="Graduation Year")

class Experience(BaseModel):
    company_name: str = Field(None, description="name of company")
    role: str = Field(None, description="role of experience")
    role_desc: str = Field(None, description="max 250 words short description of role")
    start_date: str = Field(None, description="start month and year of experience e.g. 03/2020")
    end_date: str = Field(None, description="end month and year of experience e.g. 06/2020")

class Resume(BaseModel):
    """Parsing Resume"""
    details: Candidate_Details = Field(..., description="Contains details of person as dictionary")
    education: Sequence[Education] = Field(..., description="Contains list of different educations")
    experience: Sequence[Experience] = Field(..., description="Contains list of different experiences")
    skills: str = Field(None, description="Contains technical and non technical skills separated by comma")

class Cold_Email(BaseModel):
    """Generate Cold Email"""
    subject: str = Field(..., description="Generate a short precise subject of email")
    body: str = Field(..., description="Generate short body of email describing details of resume and how they fit the job description")


parse_resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template='''You are a world class algorithm for extracting information in structured formats. Use the given format to extract information from the following input: {resume_text}. 
          Tip: Make sure to answer in the correct format. Return value of fields as None if value not found.'''
)

cold_email_prompt = PromptTemplate(
    input_variables=["applicant_details", "job_description"],
    template='''You are a world class algorithm for generating emails in structured formats. Use the given format to write cold email from the following input applicant details: {applicant_details} for job description: {job_description}. 
          Tip: Make sure to answer in the correct format. Keep the email short, on-point and explain why applicant is best fit for the role.'''
)
#ToDo
# Scrape website of company which posted job desciption and pass it to gpt