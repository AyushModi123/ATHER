from PyPDF2 import PdfReader
import os
from prompts import parse_resume_prompt, Resume
from utils.exec_prompt import exec_prompt


class data_extraction:
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
    def parse_resume(self):
        if not self.context:
            return
        try:
            document = exec_prompt(output_schema=Resume, parse_prompt=parse_resume_prompt, input_data=self.context)
        except Exception as e:  
            return e
        return document

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()    
    dt = data_extraction('Ayush_Modi_Resume_G.pdf')
    doc = dt.parse_resume()
    print(doc.education)
    print(doc.experience)
    print(doc.skills)