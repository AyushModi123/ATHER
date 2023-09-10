from PyPDF2 import PdfReader
import os
from prompts import parse_resume_prompt, cold_email_prompt, referral_email_prompt, cover_letter_prompt, ResumeSchema, EmailSchema, CoverLetterSchema
from utils.exec_prompt import exec_prompt
from utils.scraper import scrape_web

class DataExtraction:
    def __init__(self, path):        
        self.reader = PdfReader(path)
        self.num_pages = len(self.reader.pages)
        self.context = self.reader.pages[0].extract_text() # 1 page resume 
        self.links = self.extract_links()
    def extract_links(self):
        key = '/Annots'
        uri = '/URI'
        ank = '/A'
        links = []
        for page in self.reader.pages:
            pageObject = page.get_object()
            if pageObject[key]:
                ann = pageObject[key]
                for a in ann:
                    u = a.get_object()
                    if u[ank][uri]:
                        links.append(u[ank][uri])     
        return links
    def get_profile_links(self):        
        linkedin = codeforces = codechef = leetcode = github = None
        for link in self.links:
            if 'linkedin' in link:
                linkedin = link
            elif 'github' in link:
                if github and len(github) > len(link):
                    github = link
                elif not github:
                    github = link
            elif 'codeforces' in link:
                codeforces = link
            elif 'codechef' in link:
                codechef = link  
            elif 'leetcode' in link:
                leetcode = link   
        return linkedin, github, leetcode, codechef, codeforces
    def parse_resume(self):
        if not self.context:
            return
        try:
            document = exec_prompt(output_schema=ResumeSchema, parse_prompt=parse_resume_prompt, input_data={'resume_text': self.context})
        except Exception as e:  
            print("ERROR:", e)
            return None
        return document


def generate_cold_email(applicant_details, job_description, company_website_url=None):
    website_data = None
    if company_website_url:
        try:
            website_data = scrape_web(url=company_website_url)
        except Exception as e:    
            print(e)
            website_data = None
    try:
        document = exec_prompt(output_schema=EmailSchema, parse_prompt=cold_email_prompt, input_data={"applicant_details": applicant_details, "job_description": job_description, "website_data": website_data})
    except Exception as e:  
        print("ERROR:", e)
        return None
    return document

def generate_cover_letter(applicant_details, job_description):
    try:
        document = exec_prompt(output_schema=CoverLetterSchema, parse_prompt=cover_letter_prompt, input_data={"applicant_details": applicant_details, "job_description": job_description})
    except Exception as e:  
        print("ERROR:", e)
        return None
    return document

def generate_referral_email(applicant_details, job_role):
    try:
        document = exec_prompt(output_schema=EmailSchema, parse_prompt=referral_email_prompt, input_data={"applicant_details": applicant_details, "job_role": job_role})
    except Exception as e:  
        print("ERROR:", e)
        return None
    return document

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()    
    dt = DataExtraction('Ayush_Modi_Resume_G.pdf')
    doc = dt.parse_resume()
    print(doc.details)
    print(doc.education)
    print(doc.experience)
    print(doc.skills)