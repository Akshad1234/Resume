import os
import re
import cv2
import json
import pytesseract
import requests
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def clean_extracted_text(text):
    if not text:
        return ""
    text = re.sub(r'\s*\|\s*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def extract_text(file_path, file_type):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_type == "pdf":
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() or "" for page in reader.pages])
    elif file_type in ["docx", "doc"]:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif file_type in ["png", "jpg", "jpeg"]:
        img = cv2.imread(file_path)
        text = pytesseract.image_to_string(img)
    else:
        raise ValueError("Unsupported file type")
    return clean_extracted_text(text)

def check_github_strength(github_url):
    if not github_url:
        return False
    username = github_url.split("github.com/")[-1]
    api_url = f"https://api.github.com/users/{username}"
    response = requests.get(api_url)
    return response.status_code == 200 and response.json().get("public_repos", 0) >= 5

def extract_and_highlight_keywords(text):
    keywords = r'\b(' + '|'.join([
        'python', 'java', 'c\+\+', 'c#', 'javascript', 'sql', 'aws', 'azure', 'tensorflow', 'keras',
        'pandas', 'numpy', 'ml', 'ai', 'deep learning', 'data science'
    ]) + r')\b'
    github_pattern = r'https?://github\.com/[^\s]+'
    linkedin_pattern = r'https?://www\.linkedin\.com/in/[^\s]+'
    matched_keywords = [match.group() for match in re.finditer(keywords, text, re.IGNORECASE)]
    github_link = re.search(github_pattern, text)
    linkedin_link = re.search(linkedin_pattern, text)
    github_url = github_link.group() if github_link else None
    linkedin_url = linkedin_link.group() if linkedin_link else None
    github_strong = check_github_strength(github_url) if github_url else False
    selection_status = "Selected" if matched_keywords and (github_strong or linkedin_url) else "Not Selected"
    return selection_status, matched_keywords, github_url, linkedin_url

def job_role_matching(resume_text, job_desc):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_desc])
    return round(cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0] * 100, 2)

def evaluate_resume(file_path, file_type, job_description):
    try:
        resume_text = extract_text(file_path, file_type)
        selection_status, matched_keywords, github_url, linkedin_url = extract_and_highlight_keywords(resume_text)
        similarity_score = job_role_matching(resume_text, job_description)
        return {
            "Selection Status": selection_status,
            "Matched Keywords": matched_keywords,
            "Job Match Score (%)": similarity_score,
            "GitHub Profile": f"<a href='{github_url}' target='_blank'>{github_url}</a>" if github_url else "Not Provided",
            "LinkedIn Profile": f"<a href='{linkedin_url}' target='_blank'>{linkedin_url}</a>" if linkedin_url else "Not Provided"
        }
    except Exception as e:
        return {"Error": str(e)}

if __name__ == "__main__":
    file_path = r"C:\Users\akalo\OneDrive\Desktop\Resume-Shotlister\static\images\Resume (1).docx"
    file_type = "docx"
    job_desc = "Looking for a Python developer with expertise in Machine Learning, SQL, and Cloud Computing."
    result = evaluate_resume(file_path, file_type, job_desc)
    print(json.dumps(result, indent=4, ensure_ascii=False))
