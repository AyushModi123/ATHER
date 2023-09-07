from PyPDF2 import PdfReader
import os
from prompts import parse_resume_prompt, cold_email_prompt, referral_email_prompt, Resume, Email
from utils.exec_prompt import exec_prompt


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
            document = exec_prompt(output_schema=Resume, parse_prompt=parse_resume_prompt, input_data={'resume_text': self.context})
        except Exception as e:  
            print("ERROR:", e)
            return None
        return document


def generate_cold_email(applicant_details, job_description):
    try:
        document = exec_prompt(output_schema=Email, parse_prompt=cold_email_prompt, input_data={"applicant_details": applicant_details, "job_description": job_description})
    except Exception as e:  
        print("ERROR:", e)
        return None
    return document

def generate_referral_email(applicant_details, job_title):
    try:
        document = exec_prompt(output_schema=Email, parse_prompt=referral_email_prompt, input_data={"applicant_details": applicant_details, "job_title": job_title})
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