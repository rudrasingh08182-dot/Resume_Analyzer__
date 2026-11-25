from fastapi import FastAPI,UploadFile, File,HTTPException
import pymupdf
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
from io import BytesIO
import joblib
import re

app = FastAPI(title="Resume AnalyzerAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#model load
model=joblib.load("resume_rf_model.pkl")
#load Term Frequency-Inverse Document Frequency (TF-IDF) vectorizer

tfidf = joblib.load("resume_tfidf.pkl")
@app.get("/")
def home():
    return {"message":"Resume Analyzer API is running"}

def extract_text_from_pdf(file_bytes):
   text=""
   pdf =pymupdf.open(stream=file_bytes,filetype="pdf")
   for page in pdf:
       text+= page.get_text()

   pdf.close()   
   return text

def extract_text_from_docx(file_bytes):
    doc = Document(BytesIO(file_bytes))
    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    file_bytes = await file.read()
    filename = file.filename.lower()

    # Extract text from PDF
    if filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_bytes)

    # Extract text from DOCX
    elif filename.endswith(".docx"):
        extracted_text = extract_text_from_docx(file_bytes)

    else:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )

    # Check if text is extracted
    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from this resume"
        )

    # Convert resume text into TF-IDF features
    resume_vector = tfidf.transform([extracted_text])

    # Predict resume category
    predicted_category = model.predict(resume_vector)[0]

    # Get prediction confidence
    probabilities = model.predict_proba(resume_vector)[0]
    confidence = max(probabilities) * 100

    # Extract skills from resume
    detected_skills = extract_skills(extracted_text)



    return {
        "filename": file.filename,
        "message": "Resume analyzed successfully",
        "predicted_category": predicted_category,
        "confidence": round(confidence, 2),
        "skills": detected_skills,
        "total_skills": len(detected_skills),
        "characters": len(extracted_text),
        "text_preview": extracted_text[:500]
    }


# skill extraction
# Skills database
SKILLS = [
    "Python",
    "Java",
    "C++",
    "C",
    "JavaScript",
    "TypeScript",
    "SQL",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "FastAPI",
    "Flask",
    "Django",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "NLP",
    "Natural Language Processing",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Data Science",
    "Data Analysis",
    "Power BI",
    "Tableau",
    "MongoDB",
    "MySQL",
    "PostgreSQL",
    "Firebase",
    "Git",
    "GitHub",
    "Docker",
    "AWS",
    "Azure",
    "Google Cloud",
    "REST API",
    "RAG",
    "LLM",
    "Generative AI",
    "Prompt Engineering",
    "Vector Database",
    "OpenCV",
    "Computer Vision",
    "Streamlit",
    "Tailwind CSS",
    "Next.js",
    "Express.js"
]

def extract_skills(text):
    found_skills = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills

