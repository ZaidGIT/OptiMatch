import os
import random
import csv
from utils.preprocessing import clean_text
from utils.parser import extract_text_from_docx
from utils.match import calculate_match_score

def load_resume(folder_path='data/resumes'):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.docx')]

def pick_random_resume(resume_list):
    return random.choice(resume_list)

def create_resume_csv(jd_list, resume_folder='dataset/resumes', output_file='resume_jd.csv'):
    resumes = load_resume(resume_folder)
    rows = []
    
    for jd in jd_list:
        resume_path = pick_random_resume(resumes)
        resume_text = extract_text_from_docx(resume_path)
        cleaned_resume = clean_text(resume_text)
        clean_jd = clean_text(jd['jd_text'])
        match = calculate_match_score(cleaned_resume, clean_jd)

        rows.append([os.path.basename(resume_path), cleaned_resume, jd['id'], clean_jd, match])
    with open(output_file, mode='w', newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Resume Id', 'Cleaned Resume Text', 'JD ID', 'JD Text', 'Match'])
        writer.writerows(rows)