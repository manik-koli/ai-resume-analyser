import streamlit as st
import requests
import json
import PyPDF2
import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepInFrame
from reportlab.lib.units import inch
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="AI Resume Analyser", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .main { background: linear-gradient(135deg, #e8f4fd 0%, #d6eaf8 50%, #ebf5fb 100%); min-height: 100vh; }
    .hero-wrapper {
        background: linear-gradient(135deg, #1a5276 0%, #2980b9 60%, #5dade2 100%);
        border-radius: 24px; padding: 40px 30px; text-align: center;
        margin-bottom: 30px; box-shadow: 0 20px 60px #1a527644;
        position: relative; overflow: hidden;
    }
    .hero-wrapper::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, #ffffff11 0%, transparent 60%);
        animation: shimmer 4s infinite;
    }
    @keyframes shimmer { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .hero-title { font-size: 2.8rem; font-weight: 800; color: white; margin: 0; text-shadow: 0 2px 10px #00000033; letter-spacing: -1px; }
    .hero-subtitle { color: #aed6f1; font-size: 1rem; margin-top: 8px; font-weight: 400; }
    .hero-badges { display: flex; justify-content: center; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
    .badge { background: #ffffff22; border: 1px solid #ffffff44; color: white; padding: 5px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; }
    .score-card { background: white; border-radius: 20px; padding: 24px 20px; text-align: center; box-shadow: 0 8px 30px #2980b918; border: 1px solid #d6eaf8; transition: transform 0.2s ease; }
    .score-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px #2980b928; }
    .score-number { font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #1a5276, #2980b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1; }
    .score-label { color: #7fb3d3; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 6px; font-weight: 600; }
    .section-header { font-size: 1.15rem; font-weight: 700; color: #1a5276; margin: 0 0 16px 0; padding-left: 12px; border-left: 4px solid #2980b9; }
    .rank-card { background: white; border: 1px solid #d6eaf8; border-radius: 16px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 20px #2980b912; transition: transform 0.2s ease; }
    .rank-card:hover { transform: translateY(-2px); }
    .rank-1 { border-left: 5px solid #FFD700; background: linear-gradient(135deg, #fffde7, white); }
    .rank-2 { border-left: 5px solid #90a4ae; background: linear-gradient(135deg, #f5f5f5, white); }
    .rank-3 { border-left: 5px solid #CD7F32; background: linear-gradient(135deg, #fff8f0, white); }
    .stProgress > div > div { background: linear-gradient(90deg, #1a5276, #2980b9, #5dade2) !important; border-radius: 10px !important; }
    .stProgress > div { border-radius: 10px !important; height: 10px !important; }
    div[data-testid="stFileUploader"] { background: linear-gradient(135deg, #ebf5fb, #d6eaf8); border: 2px dashed #2980b966; border-radius: 20px; padding: 20px; }
    div[data-testid="stFileUploader"]:hover { border-color: #2980b9; background: linear-gradient(135deg, #d6eaf8, #aed6f1); }
    .stButton > button { background: linear-gradient(135deg, #1a5276, #2980b9) !important; color: white !important; border: none !important; border-radius: 14px !important; font-weight: 600 !important; font-size: 1rem !important; padding: 14px !important; box-shadow: 0 8px 25px #2980b944 !important; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 12px 35px #2980b966 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #d6eaf8; border-radius: 12px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px; font-weight: 600; color: #1a5276; padding: 8px 20px; }
    .stTabs [aria-selected="true"] { background: white !important; box-shadow: 0 2px 8px #2980b922; }
    div[data-testid="stMetric"] { background: white; border-radius: 16px; padding: 16px; border: 1px solid #d6eaf8; box-shadow: 0 4px 15px #2980b912; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a5276 0%, #1f618d 50%, #2980b9 100%) !important; box-shadow: 4px 0 20px #1a527633; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] input { background: white !important; border: 1px solid #ffffff44 !important; border-radius: 10px !important; color: #1a5276 !important; }
    section[data-testid="stSidebar"] .stSelectbox > div { background: white !important; border: 1px solid #ffffff44 !important; border-radius: 10px !important; color: #1a5276 !important; }
    section[data-testid="stSidebar"] .stSelectbox > div > div { color: #1a5276 !important; }
    section[data-testid="stSidebar"] .stTextInput > div > div { background: white !important; color: #1a5276 !important; border-radius: 10px !important; }
    .stAlert { border-radius: 14px !important; border: none !important; box-shadow: 0 4px 15px #00000010 !important; }
    hr { border-color: #d6eaf8 !important; margin: 24px 0 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrapper">
    <div class="hero-title">📊 AI Resume Analyser</div>
    <div class="hero-subtitle">Smart AI-powered resume analysis for candidates & recruiters</div>
    <div class="hero-badges">
        <span class="badge">⚡ Instant Analysis</span>
        <span class="badge">🤖 Gemini AI</span>
        <span class="badge">📊 ATS Score</span>
        <span class="badge">🌍 Remote Jobs</span>
        <span class="badge">📥 PDF Report</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
with col_m2:
    mode = st.radio("Select Mode", ["👤 Candidate Mode", "🏢 Recruiter Mode"],
                    horizontal=True, label_visibility="collapsed")
st.divider()

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_image_text(uploaded_file):
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image)

def get_job_links(role, experience):
    role_url = role.replace(" ", "+")
    is_fresher = "Fresher" in experience
    links = {
        "🔗 LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={role_url}&f_WT=2",
        "🔗 Indeed": f"https://indeed.com/jobs?q={role_url}&l=Remote",
        "🔗 Naukri": f"https://www.naukri.com/{role_url}-jobs?jobType=work+from+home",
    }
    if is_fresher:
        links["🎓 Internshala"] = f"https://internshala.com/jobs/{role_url}"
        links["🎓 Fresherworld"] = f"https://www.fresherworld.com/jobs/{role_url}"
    return links

def clean_json(raw_text):
    clean = raw_text.replace("```json", "").replace("```", "").strip()
    clean = re.sub(r'[\x00-\x1f\x7f]', ' ', clean)
    return json.loads(clean)

def analyse_resume(text, role, experience, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    prompt = f"""You are an expert resume analyst.
Analyse this resume for a "{role}" position. Candidate experience level: {experience}
Instructions:
- Fresher: Focus on education, projects, certifications, learning potential
- Junior: Focus on skills, small projects, growth potential
- Mid Level: Focus on work experience, achievements, technical depth
- Senior: Focus on leadership, impact, strategic contributions
Resume: --- {text} ---
Reply ONLY in valid JSON (no markdown, no backticks):
{{"overall_score":<0-100>,"ats_score":<0-100>,"score_breakdown":{{"skills":<0-100>,"experience":<0-100>,"education":<0-100>,"formatting":<0-100>,"keywords":<0-100>}},"strengths":["s1","s2","s3"],"improvements":["i1","i2","i3"],"missing_keywords":["k1","k2","k3","k4","k5"],"present_keywords":["k1","k2","k3"],"summary":"2-3 sentence assessment","top_recommendation":"single action","fresher_tips":["t1","t2","t3"]}}"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    result = requests.post(url, json=body).json()
    if "candidates" not in result:
        raise Exception(f"API Error: {result}")
    return clean_json(result["candidates"][0]["content"]["parts"][0]["text"])

def match_resume_to_jd(resume_text, candidate_name, jd_text, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    prompt = f"""You are an expert recruiter and ATS system.
Job Description: --- {jd_text} ---
Candidate Resume ({candidate_name}): --- {resume_text} ---
Reply ONLY in valid JSON (no markdown, no backticks):
{{"candidate_name":"{candidate_name}","match_score":<0-100>,"matched_skills":["s1","s2","s3"],"missing_skills":["s1","s2","s3"],"experience_match":"Good/Partial/Poor","education_match":"Good/Partial/Poor","recommendation":"Shortlist/Maybe/Reject","reason":"2-3 sentence explanation"}}"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    result = requests.post(url, json=body).json()
    if "candidates" not in result:
        raise Exception(f"API Error: {result}")
    return clean_json(result["candidates"][0]["content"]["parts"][0]["text"])

def generate_improved_resume(resume_text, job_role, experience, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    prompt = f"""You are an expert resume writer specializing in ATS-optimized resumes.
Create a highly improved ATS-friendly resume for "{job_role}" position.
Experience level: {experience}
Original Resume: --- {resume_text} ---
Rules:
- Make ATS score 95%+ friendly
- Add relevant keywords for {job_role}
- Quantify achievements where possible
- Strong action verbs
- Choose best template based on experience:
  * Fresher/Junior → use "minimal_clean"
  * Mid Level → use "classic_single"
  * Senior → use "modern_two_column"
Reply ONLY in valid JSON (no markdown, no backticks):
{{"name":"full name","email":"email or N/A","phone":"phone or N/A","location":"location or N/A","professional_summary":"3-4 line powerful summary","skills":["skill1","skill2","skill3","skill4","skill5","skill6","skill7","skill8"],"experience":[{{"title":"Job Title","company":"Company","duration":"Start-End","achievements":["a1","a2","a3"]}}],"education":[{{"degree":"Degree","institution":"Institution","year":"Year"}}],"certifications":["cert1","cert2"],"projects":[{{"name":"Project","description":"2 line description"}}],"template":"modern_two_column or classic_single or minimal_clean"}}"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    result = requests.post(url, json=body).json()
    if "candidates" not in result:
        raise Exception(f"API Error: {result}")
    return clean_json(result["candidates"][0]["content"]["parts"][0]["text"])

def create_resume_pdf_modern(resume_data, job_role):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0)
    elements = []
    page_width, page_height = A4
    left_w = page_width * 0.63
    right_w = page_width * 0.37

    name_s = ParagraphStyle('N', fontSize=22, fontName='Helvetica-Bold', textColor=colors.white, spaceAfter=2)
    role_s = ParagraphStyle('R', fontSize=11, fontName='Helvetica', textColor=colors.HexColor('#d6eaf8'), spaceAfter=2)
    contact_s = ParagraphStyle('C', fontSize=8.5, fontName='Helvetica', textColor=colors.HexColor('#d6eaf8'), spaceAfter=2)
    sec_l = ParagraphStyle('SL', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a5276'), spaceAfter=4, spaceBefore=10)
    normal_l = ParagraphStyle('NL', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#2c3e50'), spaceAfter=3, leading=13)
    bold_l = ParagraphStyle('BL', fontSize=9.5, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a5276'), spaceAfter=1)
    comp_l = ParagraphStyle('CL', fontSize=8.5, fontName='Helvetica', textColor=colors.HexColor('#7f8c8d'), spaceAfter=3)
    sec_r = ParagraphStyle('SR', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white, spaceAfter=4, spaceBefore=10)
    normal_r = ParagraphStyle('NR', fontSize=8.5, fontName='Helvetica', textColor=colors.HexColor('#d6eaf8'), spaceAfter=3, leading=13)

    left_els = []
    left_els.append(Paragraph("EXPERIENCE", sec_l))
    left_els.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2980b9'), spaceAfter=6))
    for exp in resume_data.get('experience', []):
        left_els.append(Paragraph(exp['title'], bold_l))
        left_els.append(Paragraph(f"{exp['company']}  |  {exp['duration']}", comp_l))
        for ach in exp['achievements']:
            left_els.append(Paragraph(f"• {ach}", normal_l))
        left_els.append(Spacer(1, 6))
    if resume_data.get('projects'):
        left_els.append(Paragraph("PROJECTS", sec_l))
        left_els.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2980b9'), spaceAfter=6))
        for proj in resume_data['projects']:
            left_els.append(Paragraph(proj['name'], bold_l))
            left_els.append(Paragraph(proj['description'], normal_l))
            left_els.append(Spacer(1, 4))
    if resume_data.get('education'):
        left_els.append(Paragraph("EDUCATION", sec_l))
        left_els.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2980b9'), spaceAfter=6))
        for edu in resume_data['education']:
            left_els.append(Paragraph(edu['degree'], bold_l))
            left_els.append(Paragraph(f"{edu['institution']}  |  {edu['year']}", comp_l))

    right_els = []
    right_els.append(Paragraph("SUMMARY", sec_r))
    right_els.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#5dade2'), spaceAfter=5))
    right_els.append(Paragraph(resume_data.get('professional_summary', ''), normal_r))
    right_els.append(Spacer(1, 8))
    right_els.append(Paragraph("SKILLS", sec_r))
    right_els.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#5dade2'), spaceAfter=5))
    for skill in resume_data.get('skills', []):
        right_els.append(Paragraph(f"◆  {skill}", normal_r))
    if resume_data.get('certifications') and resume_data['certifications']:
        right_els.append(Spacer(1, 8))
        right_els.append(Paragraph("CERTIFICATIONS", sec_r))
        right_els.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#5dade2'), spaceAfter=5))
        for cert in resume_data['certifications']:
            right_els.append(Paragraph(f"◆  {cert}", normal_r))

    left_frame = KeepInFrame(left_w - 50, page_height - 120, left_els, mode='shrink')
    right_frame = KeepInFrame(right_w - 30, page_height - 120, right_els, mode='shrink')

    header = Table([[Paragraph(resume_data['name'], name_s)],
                    [Paragraph(job_role.upper(), role_s)],
                    [Paragraph(f"✉ {resume_data['email']}   📱 {resume_data['phone']}   📍 {resume_data['location']}", contact_s)]],
                   colWidths=[page_width - 80])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a5276')),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 30), ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))

    body = Table([[left_frame, right_frame]], colWidths=[left_w - 10, right_w])
    body.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.white),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#1f618d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (0,0), 20), ('BOTTOMPADDING', (0,0), (0,0), 20),
        ('LEFTPADDING', (0,0), (0,0), 30), ('RIGHTPADDING', (0,0), (0,0), 15),
        ('TOPPADDING', (1,0), (1,0), 20), ('BOTTOMPADDING', (1,0), (1,0), 20),
        ('LEFTPADDING', (1,0), (1,0), 15), ('RIGHTPADDING', (1,0), (1,0), 15),
    ]))

    footer_s = ParagraphStyle('F', fontSize=7.5, fontName='Helvetica', textColor=colors.HexColor('#aed6f1'), alignment=1)
    footer = Table([[Paragraph(f"Generated by AI Resume Analyser  |  Optimized for {job_role}", footer_s)]], colWidths=[page_width - 40])
    footer.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a5276')), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))

    elements.extend([header, body, footer])
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_resume_pdf_classic(resume_data, job_role):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=40, bottomMargin=40)
    elements = []
    name_s = ParagraphStyle('N', fontSize=22, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a5276'), spaceAfter=2, alignment=1)
    contact_s = ParagraphStyle('C', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#666666'), spaceAfter=6, alignment=1)
    sec_s = ParagraphStyle('S', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a5276'), spaceAfter=4, spaceBefore=10)
    normal_s = ParagraphStyle('N2', fontSize=9.5, fontName='Helvetica', textColor=colors.HexColor('#333333'), spaceAfter=3, leading=14)
    bold_s = ParagraphStyle('B', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a5276'), spaceAfter=2)
    comp_s = ParagraphStyle('Co', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#7f8c8d'), spaceAfter=3)
    footer_s = ParagraphStyle('F', fontSize=7.5, fontName='Helvetica', textColor=colors.HexColor('#aed6f1'), alignment=1)

    def sec(title):
        elements.append(Paragraph(title, sec_s))
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#aed6f1'), spaceAfter=5))

    elements.append(Paragraph(resume_data['name'], name_s))
    elements.append(Paragraph(f"{resume_data['email']}  |  {resume_data['phone']}  |  {resume_data['location']}", contact_s))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a5276')))
    elements.append(Spacer(1, 8))
    sec("PROFESSIONAL SUMMARY")
    elements.append(Paragraph(resume_data['professional_summary'], normal_s))
    elements.append(Spacer(1, 6))
    sec("SKILLS")
    elements.append(Paragraph("  •  ".join(resume_data['skills']), normal_s))
    elements.append(Spacer(1, 6))
    if resume_data.get('experience'):
        sec("WORK EXPERIENCE")
        for exp in resume_data['experience']:
            elements.append(Paragraph(f"{exp['title']} — {exp['company']}", bold_s))
            elements.append(Paragraph(exp['duration'], comp_s))
            for ach in exp['achievements']:
                elements.append(Paragraph(f"•  {ach}", normal_s))
            elements.append(Spacer(1, 6))
    if resume_data.get('projects'):
        sec("PROJECTS")
        for proj in resume_data['projects']:
            elements.append(Paragraph(proj['name'], bold_s))
            elements.append(Paragraph(proj['description'], normal_s))
            elements.append(Spacer(1, 4))
    if resume_data.get('education'):
        sec("EDUCATION")
        for edu in resume_data['education']:
            elements.append(Paragraph(f"{edu['degree']} — {edu['institution']}", bold_s))
            elements.append(Paragraph(edu['year'], comp_s))
    if resume_data.get('certifications') and resume_data['certifications']:
        sec("CERTIFICATIONS")
        for cert in resume_data['certifications']:
            elements.append(Paragraph(f"•  {cert}", normal_s))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#aed6f1')))
    elements.append(Paragraph(f"Generated by AI Resume Analyser  |  Optimized for {job_role}", footer_s))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_resume_pdf_minimal(resume_data, job_role):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=55, leftMargin=55, topMargin=45, bottomMargin=45)
    elements = []
    name_s = ParagraphStyle('N', fontSize=18, fontName='Helvetica-Bold', textColor=colors.HexColor('#2c3e50'), spaceAfter=6)
    contact_s = ParagraphStyle('C', fontSize=8.5, fontName='Helvetica', textColor=colors.HexColor('#7f8c8d'), spaceAfter=8)
    sec_s = ParagraphStyle('S', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#2980b9'), spaceAfter=4, spaceBefore=12)
    normal_s = ParagraphStyle('N2', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#2c3e50'), spaceAfter=3, leading=14)
    bold_s = ParagraphStyle('B', fontSize=9.5, fontName='Helvetica-Bold', textColor=colors.HexColor('#2c3e50'), spaceAfter=1)
    comp_s = ParagraphStyle('Co', fontSize=8.5, fontName='Helvetica', textColor=colors.HexColor('#95a5a6'), spaceAfter=3)

    def sec(title):
        elements.append(Paragraph(title, sec_s))
        elements.append(HRFlowable(width="30%", thickness=2, color=colors.HexColor('#2980b9'), spaceAfter=5))

    elements.append(Paragraph(resume_data['name'], name_s))
    elements.append(Paragraph(f"{resume_data['email']}   |   {resume_data['phone']}   |   {resume_data['location']}", contact_s))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#bdc3c7'), spaceAfter=8))
    sec("SUMMARY")
    elements.append(Paragraph(resume_data['professional_summary'], normal_s))
    sec("SKILLS")
    elements.append(Paragraph("  ·  ".join(resume_data['skills']), normal_s))
    if resume_data.get('experience'):
        sec("EXPERIENCE")
        for exp in resume_data['experience']:
            elements.append(Paragraph(exp['title'], bold_s))
            elements.append(Paragraph(f"{exp['company']}  ·  {exp['duration']}", comp_s))
            for ach in exp['achievements']:
                elements.append(Paragraph(f"– {ach}", normal_s))
            elements.append(Spacer(1, 5))
    if resume_data.get('projects'):
        sec("PROJECTS")
        for proj in resume_data['projects']:
            elements.append(Paragraph(proj['name'], bold_s))
            elements.append(Paragraph(proj['description'], normal_s))
            elements.append(Spacer(1, 4))
    if resume_data.get('education'):
        sec("EDUCATION")
        for edu in resume_data['education']:
            elements.append(Paragraph(edu['degree'], bold_s))
            elements.append(Paragraph(f"{edu['institution']}  ·  {edu['year']}", comp_s))
    if resume_data.get('certifications') and resume_data['certifications']:
        sec("CERTIFICATIONS")
        for cert in resume_data['certifications']:
            elements.append(Paragraph(f"› {cert}", normal_s))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_pdf_report(data, job_role, experience):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#1a5276'), spaceAfter=5, fontName='Helvetica-Bold')
    heading_s = ParagraphStyle('H', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2980b9'), spaceBefore=15, spaceAfter=5, fontName='Helvetica-Bold')
    normal_s = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#333333'), spaceAfter=4, fontName='Helvetica')

    elements.append(Paragraph("AI Resume Analysis Report", title_s))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_s))
    elements.append(Paragraph(f"Target Role: {job_role}  |  Experience: {experience}", normal_s))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Overall Scores", heading_s))
    score_data = [['Metric', 'Score'], ['Overall Score', f"{data['overall_score']}/100"], ['ATS Score', f"{data['ats_score']}/100"]]
    t = Table(score_data, colWidths=[3*inch, 2*inch])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a5276')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),11),('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#d6eaf8'),colors.white]),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#aed6f1')),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    elements.append(t)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Score Breakdown", heading_s))
    bd = [['Category', 'Score']] + [[k.capitalize(), f"{v}/100"] for k,v in data["score_breakdown"].items()]
    t2 = Table(bd, colWidths=[3*inch, 2*inch])
    t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2980b9')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#ebf5fb'),colors.white]),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#aed6f1')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    elements.append(t2)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Strengths", heading_s))
    for s in data["strengths"]: elements.append(Paragraph(f"✓  {s}", normal_s))
    elements.append(Paragraph("Improvements Needed", heading_s))
    for i in data["improvements"]: elements.append(Paragraph(f"→  {i}", normal_s))
    if "Fresher" in experience or "Junior" in experience:
        elements.append(Paragraph("Fresher Tips", heading_s))
        for tip in data.get("fresher_tips", []): elements.append(Paragraph(f"•  {tip}", normal_s))
    elements.append(Paragraph("Present Keywords", heading_s))
    elements.append(Paragraph(", ".join(data["present_keywords"]), normal_s))
    elements.append(Paragraph("Missing Keywords", heading_s))
    elements.append(Paragraph(", ".join(data["missing_keywords"]), normal_s))
    elements.append(Paragraph("Summary", heading_s))
    elements.append(Paragraph(data["summary"], normal_s))
    elements.append(Paragraph("Top Recommendation", heading_s))
    elements.append(Paragraph(data["top_recommendation"], normal_s))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_recruiter_pdf(results, jd_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#1a5276'), spaceAfter=5, fontName='Helvetica-Bold')
    heading_s = ParagraphStyle('H', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2980b9'), spaceBefore=15, spaceAfter=5, fontName='Helvetica-Bold')
    normal_s = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#333333'), spaceAfter=4, fontName='Helvetica')
    elements.append(Paragraph("Recruiter Screening Report", title_s))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_s))
    elements.append(Paragraph(f"Total Candidates: {len(results)}", normal_s))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Candidate Rankings", heading_s))
    rank_data = [['Rank', 'Candidate', 'Match Score', 'Recommendation']] + [[f"#{i+1}", r['candidate_name'], f"{r['match_score']}%", r['recommendation']] for i,r in enumerate(results)]
    rt = Table(rank_data, colWidths=[0.8*inch, 2.5*inch, 1.5*inch, 1.8*inch])
    rt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a5276')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#d6eaf8'),colors.white]),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#aed6f1')),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    elements.append(rt)
    elements.append(Spacer(1, 15))
    for i, r in enumerate(results):
        elements.append(Paragraph(f"#{i+1} — {r['candidate_name']} ({r['match_score']}% match)", heading_s))
        elements.append(Paragraph(f"Recommendation: {r['recommendation']}", normal_s))
        elements.append(Paragraph(f"Experience: {r['experience_match']}  |  Education: {r['education_match']}", normal_s))
        elements.append(Paragraph(f"Reason: {r['reason']}", normal_s))
        elements.append(Paragraph(f"Matched: {', '.join(r['matched_skills'])}", normal_s))
        elements.append(Paragraph(f"Missing: {', '.join(r['missing_skills'])}", normal_s))
        elements.append(Spacer(1, 8))
    doc.build(elements)
    buffer.seek(0)
    return buffer


# CANDIDATE MODE
if mode == "👤 Candidate Mode":
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.divider()
        api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIzaSy...")
        st.caption("Get free key at aistudio.google.com")
        st.divider()
        job_role = st.text_input("🎯 Target Job Role", placeholder="e.g. Data Analyst, HR Manager...")
        experience = st.selectbox("👤 Experience Level", [
            "Fresher (0-1 years)", "Junior (1-3 years)",
            "Mid Level (3-5 years)", "Senior (5+ years)"
        ])
        st.divider()
        st.markdown("### 📌 How to use")
        st.markdown("""
        1. Enter Gemini API key
        2. Type your target job role
        3. Select experience level
        4. Upload resume PDF or Image
        5. Click Analyse!
        6. Download PDF report
        """)

    st.markdown('<p class="section-header">📄 Upload Resume</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📄 PDF Upload", "🖼️ Image Upload (JPG/PNG)"])
    resume_text = ""

    with tab1:
        uploaded_file = st.file_uploader("Drag & drop your resume PDF here", type=["pdf"], help="Max 20MB")
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 20:
                st.error("❌ File too large!")
            else:
                resume_text = extract_pdf_text(uploaded_file)
                c1, c2, c3 = st.columns(3)
                c1.metric("📄 File", uploaded_file.name[:20] + "...")
                c2.metric("📦 Size", f"{file_size_mb:.2f} MB")
                c3.metric("📝 Characters", len(resume_text))
                st.success("✅ PDF loaded successfully!")

    with tab2:
        uploaded_image = st.file_uploader("Drag & drop your resume image here", type=["jpg", "jpeg", "png"], help="Max 20MB")
        if uploaded_image:
            file_size_mb = uploaded_image.size / (1024 * 1024)
            if file_size_mb > 20:
                st.error("❌ File too large!")
            else:
                col_img, col_info = st.columns([1, 1])
                with col_img:
                    st.image(uploaded_image, caption="Uploaded Resume", use_column_width=True)
                with col_info:
                    with st.spinner("🔍 Extracting text..."):
                        resume_text = extract_image_text(uploaded_image)
                    if resume_text.strip():
                        st.metric("📝 Characters Found", len(resume_text))
                        st.success("✅ Image loaded successfully!")
                    else:
                        st.error("❌ Text extract nahi hua!")

    st.divider()

    if 'improved_pdf' not in st.session_state:
        st.session_state.improved_pdf = None
    if 'improved_name' not in st.session_state:
        st.session_state.improved_name = None

    if st.button("🔍 Analyse My Resume", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please enter your API Key!")
        elif not job_role:
            st.error("❌ Please enter your target job role!")
        elif not resume_text:
            st.error("❌ Please upload your resume!")
        else:
            with st.spinner("🤖 AI is analysing your resume..."):
                try:
                    data = analyse_resume(resume_text, job_role, experience, api_key)
                    st.session_state['analysis_data'] = data
                    st.session_state['resume_text'] = resume_text
                    st.session_state['job_role'] = job_role
                    st.session_state['experience'] = experience
                    st.session_state['api_key'] = api_key
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'analysis_data' in st.session_state:
        data = st.session_state['analysis_data']
        job_role = st.session_state['job_role']
        experience = st.session_state['experience']
        resume_text = st.session_state['resume_text']
        api_key = st.session_state['api_key']

        st.divider()
        st.markdown('<p class="section-header">🎯 Overall Scores</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="score-card"><div class="score-number">{data["overall_score"]}</div><div class="score-label">Overall Score</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="score-card"><div class="score-number">{data["ats_score"]}</div><div class="score-label">ATS Score</div></div>', unsafe_allow_html=True)
        with col3:
            status = 'Strong 💪' if data['overall_score'] >= 70 else 'Average 📈' if data['overall_score'] >= 50 else 'Needs Work 🔧'
            st.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.4rem">{status}</div><div class="score-label">Profile Status</div></div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<p class="section-header">📈 Score Breakdown</p>', unsafe_allow_html=True)
        for label, val in data["score_breakdown"].items():
            cl, cr = st.columns([4, 1])
            with cl: st.progress(val / 100)
            with cr: st.write(f"**{label.capitalize()}** {val}/100")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p class="section-header">✅ Strengths</p>', unsafe_allow_html=True)
            for s in data["strengths"]: st.success(s)
        with col_b:
            st.markdown('<p class="section-header">⚠️ Improvements</p>', unsafe_allow_html=True)
            for i in data["improvements"]: st.warning(i)

        if "Fresher" in experience or "Junior" in experience:
            st.divider()
            st.markdown('<p class="section-header">🎓 Fresher Tips</p>', unsafe_allow_html=True)
            for tip in data.get("fresher_tips", []): st.info(f"💡 {tip}")

        st.divider()
        st.markdown('<p class="section-header">🏷️ Keywords Analysis</p>', unsafe_allow_html=True)
        ck1, ck2 = st.columns(2)
        with ck1:
            st.markdown("**✅ Present Keywords**")
            st.write("  ".join([f"`{k}`" for k in data["present_keywords"]]))
        with ck2:
            st.markdown("**❌ Missing Keywords**")
            st.write("  ".join([f"`{k}`" for k in data["missing_keywords"]]))

        st.divider()
        st.markdown('<p class="section-header">🌍 Remote Job Opportunities</p>', unsafe_allow_html=True)
        job_links = get_job_links(job_role, experience)
        jcols = st.columns(len(job_links))
        for i, (name, link) in enumerate(job_links.items()):
            with jcols[i]: st.link_button(name, link, use_container_width=True)

        st.divider()
        st.markdown('<p class="section-header">📝 Summary</p>', unsafe_allow_html=True)
        st.info(data["summary"])
        st.markdown('<p class="section-header">🚀 Top Recommendation</p>', unsafe_allow_html=True)
        st.warning(data["top_recommendation"])

        st.divider()
        st.markdown('<p class="section-header">✨ Get Your Improved Resume</p>', unsafe_allow_html=True)
        st.info("🤖 AI will auto-select the best template and rewrite your resume with 95%+ ATS score!")

        if st.button("🚀 Generate Improved Resume", use_container_width=True, key="gen_improve"):
            with st.spinner("✨ AI is rewriting your resume..."):
                try:
                    improved_data = generate_improved_resume(resume_text, job_role, experience, api_key)
                    template = improved_data.get('template', 'modern_two_column')
                    if template == 'classic_single':
                        resume_pdf = create_resume_pdf_classic(improved_data, job_role)
                        template_name = "Classic Single Column"
                    elif template == 'minimal_clean':
                        resume_pdf = create_resume_pdf_minimal(improved_data, job_role)
                        template_name = "Minimal Clean"
                    else:
                        resume_pdf = create_resume_pdf_modern(improved_data, job_role)
                        template_name = "Modern Two Column"
                    st.session_state.improved_pdf = resume_pdf
                    st.session_state.improved_name = improved_data['name'].replace(' ', '_')
                    st.success(f"✅ Resume ready! Template: **{template_name}**")
                    col_r1, col_r2 = st.columns(2)
                    with col_r1: st.metric("🎯 Expected ATS Score", "95%+")
                    with col_r2: st.metric("🎨 Template", template_name)
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.improved_pdf is not None:
            st.download_button(
                label="📥 Download Improved Resume (PDF)",
                data=st.session_state.improved_pdf,
                file_name=f"improved_resume_{st.session_state.improved_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_improved"
            )

        st.divider()
        st.markdown('<p class="section-header">📥 Download Analysis Report</p>', unsafe_allow_html=True)
        pdf_buffer = generate_pdf_report(data, job_role, experience)
        st.download_button(
            label="📥 Download Full Report (PDF)",
            data=pdf_buffer,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# RECRUITER MODE
elif mode == "🏢 Recruiter Mode":
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.divider()
        api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIzaSy...")
        st.caption("Get free key at aistudio.google.com")
        st.divider()
        st.markdown("### 📌 How to use")
        st.markdown("""
        1. Enter Gemini API key
        2. Paste the Job Description
        3. Upload up to 5 resumes
        4. Click Screen Candidates!
        5. See ranked results
        6. Download screening report
        """)

    st.markdown('<p class="section-header">📋 Job Description</p>', unsafe_allow_html=True)
    jd_text = st.text_area("Paste the Job Description here", height=200,
                            placeholder="Paste the full job description here...")

    st.divider()
    st.markdown('<p class="section-header">📁 Upload Candidate Resumes (Max 5)</p>', unsafe_allow_html=True)
    uploaded_resumes = st.file_uploader("Upload up to 5 resume PDFs", type=["pdf"], accept_multiple_files=True)

    if uploaded_resumes:
        if len(uploaded_resumes) > 5:
            st.warning("⚠️ Maximum 5 resumes allowed.")
            uploaded_resumes = uploaded_resumes[:5]
        st.success(f"✅ {len(uploaded_resumes)} resume(s) uploaded!")
        for f in uploaded_resumes:
            st.caption(f"📄 {f.name}")

    st.divider()
    if st.button("🔍 Screen Candidates", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please enter your API Key!")
        elif not jd_text:
            st.error("❌ Please paste the Job Description!")
        elif not uploaded_resumes:
            st.error("❌ Please upload at least one resume!")
        else:
            results = []
            progress_bar = st.progress(0, text="Screening candidates...")
            for i, resume_file in enumerate(uploaded_resumes):
                candidate_name = resume_file.name.replace(".pdf", "").replace("_", " ")
                resume_text = extract_pdf_text(resume_file)
                progress_bar.progress((i + 1) / len(uploaded_resumes), text=f"Analysing {candidate_name}...")
                try:
                    result = match_resume_to_jd(resume_text, candidate_name, jd_text, api_key)
                    results.append(result)
                except Exception as e:
                    st.error(f"Error: {e}")

            progress_bar.empty()
            results = sorted(results, key=lambda x: x["match_score"], reverse=True)

            st.divider()
            st.markdown('<p class="section-header">🏆 Candidate Rankings</p>', unsafe_allow_html=True)
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            rank_classes = ["rank-1", "rank-2", "rank-3", "rank-card", "rank-card"]
            rec_colors = {"Shortlist": "✅ Shortlist", "Maybe": "🟡 Maybe", "Reject": "❌ Reject"}

            for i, r in enumerate(results):
                medal = medals[i] if i < len(medals) else f"#{i+1}"
                rec = rec_colors.get(r["recommendation"], r["recommendation"])
                st.markdown(f"""
                <div class="rank-card {rank_classes[i]}">
                    <h3>{medal} {r['candidate_name']} — {r['match_score']}% Match</h3>
                    <p><b>Recommendation:</b> {rec} &nbsp;|&nbsp;
                    <b>Experience:</b> {r['experience_match']} &nbsp;|&nbsp;
                    <b>Education:</b> {r['education_match']}</p>
                    <p>{r['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander(f"View details — {r['candidate_name']}"):
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        st.markdown("**✅ Matched Skills**")
                        for s in r["matched_skills"]: st.success(s)
                    with dc2:
                        st.markdown("**❌ Missing Skills**")
                        for s in r["missing_skills"]: st.warning(s)

            st.divider()
            st.markdown('<p class="section-header">📥 Download Screening Report</p>', unsafe_allow_html=True)
            pdf_buffer = generate_recruiter_pdf(results, jd_text)
            st.download_button(
                label="📥 Download Screening Report (PDF)",
                data=pdf_buffer,
                file_name=f"recruiter_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )