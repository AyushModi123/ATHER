from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from typing import Optional, Sequence
from pydantic import BaseModel, Field


class Education(BaseModel):
    name: str = Field(..., description="name of college or school")
    stream: str = Field(..., description="stream of education")
    score: int = Field(..., description="contains score in this institute")
    location: str = Field(..., description="Location of institute")
    graduation_year: int = Field(..., description="Graduation Year")

class Experience(BaseModel):
    company_name: str = Field(..., description="name of company")
    role: str = Field(..., description="role of experience")
    role_desc: str = Field(..., description="max 250 words short description of role")
    start_date: str = Field(..., description="start month and year of experience e.g. 03/2020")
    end_date: str = Field(..., description="end month and year of experience e.g. 06/2020")


class Resume(BaseModel):
    """Parsing Resume"""

    education: Sequence[Education] = Field(..., description="Contains list of different educations")
    experience: Sequence[Experience] = Field(..., description="Contains list of different experiences. NA if not found.")
    skills: str = Field(..., description="Contains technical and non technical skills separated by comma")


parse_resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template='''You are a world class algorithm for extracting information in structured formats. Use the given format to extract information from the following input: {resume_text}. 
          Tip: Make sure to answer in the correct format. Return value of fields as NA if value not found.'''
)

