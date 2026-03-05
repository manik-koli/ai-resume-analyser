import streamlit as st
import requests
import json
import PyPDF2
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


st.set_page_config(
    page_title="AI Resume Analyser",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Poppins', sans-serif; }

    .main {
        background: linear-gradient(135deg, #e8f4fd 0%, #d6eaf8 50%, #ebf5fb 100%);
        min-height: 100vh;
    }

    .hero-wrapper {
        background: linear-gradient(135deg, #1a5276 0%, #2980b9 60%, #5dade2 100%);
        border-radius: 24px;
        padding: 40px 30px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 20px 60px #1a527644;
        position: relative;
        overflow: hidden;
    }
    .hero-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, #ffffff11 0%, transparent 60%);
        animation: shimmer 4s infinite;
    }
    @keyframes shimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 2px 10px #00000033;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        color: #aed6f1;
        font-size: 1rem;
        margin-top: 8px;
        font-weight: 400;
    }
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 16px;
        flex-wrap: wrap;
    }
    .badge {
        background: #ffffff22;
        border: 1px solid #ffffff44;
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }

    .score-card {
        background: white;
        border-radius: 20px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 8px 30px #2980b918;
        border: 1px solid #d6eaf8;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .score-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 40px #2980b928;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1a5276, #2980b9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .score-label {
        color: #7fb3d3;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 6px;
        font-weight: 600;
    }

    .section-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px #2980b912;
        border: 1px solid #d6eaf8;
    }
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a5276;
        margin: 0 0 16px 0;
        padding-left: 12px;
        border-left: 4px solid #2980b9;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .rank-card {
        background: white;
        border: 1px solid #d6eaf8;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px #2980b912;
        transition: transform 0.2s ease;
    }
    .rank-card:hover { transform: translateY(-2px); }
    .rank-1 { border-left: 5px solid #FFD700; background: linear-gradient(135deg, #fffde7, white); }
    .rank-2 { border-left: 5px solid #90a4ae; background: linear-gradient(135deg, #f5f5f5, white); }
    .rank-3 { border-left: 5px solid #CD7F32; background: linear-gradient(135deg, #fff8f0, white); }

    .stProgress > div > div {
        background: linear-gradient(90deg, #1a5276, #2980b9, #5dade2) !important;
        border-radius: 10px !important;
        transition: width 1s ease !important;
    }
    .stProgress > div {
        border-radius: 10px !important;
        height: 10px !important;
    }

    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #ebf5fb, #d6eaf8);
        border: 2px dashed #2980b966;
        border-radius: 20px;
        padding: 20px;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #2980b9;
        background: linear-gradient(135deg, #d6eaf8, #aed6f1);
    }

    .stButton > button {
        background: linear-gradient(135deg, #1a5276, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 14px !important;
        box-shadow: 0 8px 25px #2980b944 !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px #2980b966 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #d6eaf8;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        color: #1a5276;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        box-shadow: 0 2px 8px #2980b922;
    }

    div[data-testid="stMetric"] {
        background: white;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #d6eaf8;
        box-shadow: 0 4px 15px #2980b912;
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a5276 0%, #1f618d 50%, #2980b9 100%) !important;
        box-shadow: 4px 0 20px #1a527633;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    section[data-testid="stSidebar"] input {
        background: #ffffff22 !important;
        border: 1px solid #ffffff44 !important;
        border-radius: 10px !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div {
        background: #ffffff22 !important;
        border: 1px solid #ffffff44 !important;
        border-radius: 10px !important;
    }

    .stAlert {
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 15px #00000010 !important;
    }

    hr {
        border-color: #d6eaf8 !important;
        margin: 24px 0 !important;
    }
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
    mode = st.radio(
        "Select Mode",
        ["👤 Candidate Mode", "🏢 Recruiter Mode"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.divider()

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_image_text(uploaded_file):
    image = Image.open(uploaded_file)
    text = pytesseract.image_to_string(image)
    return text

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

def analyse_resume(text, role, experience, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    prompt = f"""You are an expert resume analyst.
Analyse this resume for a "{role}" position.
Candidate experience level: {experience}

Instructions:
- Fresher: Focus on education, projects, certifications, learning potential
- Junior: Focus on skills, small projects, growth potential
- Mid Level: Focus on work experience, achievements, technical depth
- Senior: Focus on leadership, impact, strategic contributions

Resume:
---
{text}
---

Reply ONLY in valid JSON (no markdown, no backticks):
{{
  "overall_score": <0-100>,
  "ats_score": <0-100>,
  "score_breakdown": {{
    "skills": <0-100>,
    "experience": <0-100>,
    "education": <0-100>,
    "formatting": <0-100>,
    "keywords": <0-100>
  }},
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "missing_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "present_keywords": ["keyword1", "keyword2", "keyword3"],
  "summary": "2-3 sentence overall assessment",
  "top_recommendation": "single most important action",
  "fresher_tips": ["tip1", "tip2", "tip3"]
}}"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=body)
    result = response.json()
    if "candidates" not in result:
        raise Exception(f"API Error: {result}")
    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
    clean = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def match_resume_to_jd(resume_text, candidate_name, jd_text, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    prompt = f"""You are an expert recruiter and ATS system.

Job Description:
---
{jd_text}
---

Candidate Resume ({candidate_name}):
---
{resume_text}
---

Analyse how well this resume matches the job description.
Reply ONLY in valid JSON (no markdown, no backticks):
{{
  "candidate_name": "{candidate_name}",
  "match_score": <0-100>,
  "matched_skills": ["skill1", "skill2", "skill3"],
  "missing_skills": ["skill1", "skill2", "skill3"],
  "experience_match": "Good/Partial/Poor",
  "education_match": "Good/Partial/Poor",
  "recommendation": "Shortlist/Maybe/Reject",
  "reason": "2-3 sentence explanation of match"
}}"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=body)
    result = response.json()
    if "candidates" not in result:
        raise Exception(f"API Error: {result}")
    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
    clean = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def generate_pdf_report(data, job_role, experience):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []
    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#1a5276'),
        spaceAfter=5, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#2980b9'),
        spaceBefore=15, spaceAfter=5, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#333333'),
        spaceAfter=4, fontName='Helvetica')

    elements.append(Paragraph("AI Resume Analysis Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    elements.append(Paragraph(f"Target Role: {job_role}  |  Experience: {experience}", normal_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Overall Scores", heading_style))
    score_data = [['Metric', 'Score'],
                  ['Overall Score', f"{data['overall_score']}/100"],
                  ['ATS Score', f"{data['ats_score']}/100"]]
    score_table = Table(score_data, colWidths=[3*inch, 2*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#d6eaf8'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#aed6f1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Score Breakdown", heading_style))
    breakdown_data = [['Category', 'Score']]
    for label, val in data["score_breakdown"].items():
        breakdown_data.append([label.capitalize(), f"{val}/100"])
    breakdown_table = Table(breakdown_data, colWidths=[3*inch, 2*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ebf5fb'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#aed6f1')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    elements.append(breakdown_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Strengths", heading_style))
    for s in data["strengths"]:
        elements.append(Paragraph(f"✓  {s}", normal_style))

    elements.append(Paragraph("Improvements Needed", heading_style))
    for i in data["improvements"]:
        elements.append(Paragraph(f"→  {i}", normal_style))

    if "Fresher" in experience or "Junior" in experience:
        elements.append(Paragraph("Fresher Tips", heading_style))
        for tip in data.get("fresher_tips", []):
            elements.append(Paragraph(f"•  {tip}", normal_style))

    elements.append(Paragraph("Present Keywords", heading_style))
    elements.append(Paragraph(", ".join(data["present_keywords"]), normal_style))
    elements.append(Paragraph("Missing Keywords", heading_style))
    elements.append(Paragraph(", ".join(data["missing_keywords"]), normal_style))
    elements.append(Paragraph("Summary", heading_style))
    elements.append(Paragraph(data["summary"], normal_style))
    elements.append(Paragraph("Top Recommendation", heading_style))
    elements.append(Paragraph(data["top_recommendation"], normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_recruiter_pdf(results, jd_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []
    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#1a5276'),
        spaceAfter=5, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#2980b9'),
        spaceBefore=15, spaceAfter=5, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#333333'),
        spaceAfter=4, fontName='Helvetica')

    elements.append(Paragraph("Recruiter Screening Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    elements.append(Paragraph(f"Total Candidates Screened: {len(results)}", normal_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Candidate Rankings", heading_style))
    rank_data = [['Rank', 'Candidate', 'Match Score', 'Recommendation']]
    for i, r in enumerate(results):
        rank_data.append([f"#{i+1}", r['candidate_name'], f"{r['match_score']}%", r['recommendation']])
    rank_table = Table(rank_data, colWidths=[0.8*inch, 2.5*inch, 1.5*inch, 1.8*inch])
    rank_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#d6eaf8'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#aed6f1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(rank_table)
    elements.append(Spacer(1, 15))

    for i, r in enumerate(results):
        elements.append(Paragraph(f"#{i+1} — {r['candidate_name']} ({r['match_score']}% match)", heading_style))
        elements.append(Paragraph(f"Recommendation: {r['recommendation']}", normal_style))
        elements.append(Paragraph(f"Experience Match: {r['experience_match']}  |  Education Match: {r['education_match']}", normal_style))
        elements.append(Paragraph(f"Reason: {r['reason']}", normal_style))
        elements.append(Paragraph(f"Matched Skills: {', '.join(r['matched_skills'])}", normal_style))
        elements.append(Paragraph(f"Missing Skills: {', '.join(r['missing_skills'])}", normal_style))
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
            "Fresher (0-1 years)",
            "Junior (1-3 years)",
            "Mid Level (3-5 years)",
            "Senior (5+ years)"
        ])
        st.divider()
        st.markdown("### 📌 How to use")
        st.markdown("""
        1. Enter Gemini API key
        2. Type your target job role
        3. Select experience level
        4. Upload resume PDF
        5. Click Analyse!
        6. Download PDF report
        """)

    st.markdown('<p class="section-header">📄 Upload Resume</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📄 PDF Upload", "🖼️ Image Upload (JPG/PNG)"])
    resume_text = ""

    with tab1:
        uploaded_file = st.file_uploader(
            "Drag & drop your resume PDF here",
            type=["pdf"],
            help="Maximum file size: 20MB"
        )
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 20:
                st.error("❌ File too large! Maximum size is 20MB.")
            else:
                resume_text = extract_pdf_text(uploaded_file)
                c1, c2, c3 = st.columns(3)
                c1.metric("📄 File", uploaded_file.name[:20] + "...")
                c2.metric("📦 Size", f"{file_size_mb:.2f} MB")
                c3.metric("📝 Characters", len(resume_text))
                st.success("✅ PDF loaded successfully!")

    with tab2:
        uploaded_image = st.file_uploader(
            "Drag & drop your resume image here",
            type=["jpg", "jpeg", "png"],
            help="Maximum file size: 20MB"
        )
        if uploaded_image:
            file_size_mb = uploaded_image.size / (1024 * 1024)
            if file_size_mb > 20:
                st.error("❌ File too large! Maximum size is 20MB.")
            else:
                col_img, col_info = st.columns([1, 1])
                with col_img:
                    st.image(uploaded_image, caption="Uploaded Resume", use_column_width=True)
                with col_info:
                    with st.spinner("🔍 Extracting text from image..."):
                        resume_text = extract_image_text(uploaded_image)
                    if resume_text.strip():
                        st.metric("📝 Characters Found", len(resume_text))
                        st.success("✅ Image loaded successfully!")
                    else:
                        st.error("❌ Text extract nahi hua! Clear image upload karo.")

    st.divider()
    if st.button("🔍 Analyse My Resume", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please enter your API Key in the sidebar!")
        elif not job_role:
            st.error("❌ Please enter your target job role!")
        elif not resume_text:
            st.error("❌ Please upload your resume or paste the text!")
        else:
            with st.spinner("🤖 AI is analysing your resume..."):
                try:
                    data = analyse_resume(resume_text, job_role, experience, api_key)

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
                        with cl:
                            st.progress(val / 100)
                        with cr:
                            st.write(f"**{label.capitalize()}** {val}/100")

                    st.divider()
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown('<p class="section-header">✅ Strengths</p>', unsafe_allow_html=True)
                        for s in data["strengths"]:
                            st.success(s)
                    with col_b:
                        st.markdown('<p class="section-header">⚠️ Improvements</p>', unsafe_allow_html=True)
                        for i in data["improvements"]:
                            st.warning(i)

                    if "Fresher" in experience or "Junior" in experience:
                        st.divider()
                        st.markdown('<p class="section-header">🎓 Fresher Tips</p>', unsafe_allow_html=True)
                        for tip in data.get("fresher_tips", []):
                            st.info(f"💡 {tip}")

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
                        with jcols[i]:
                            st.link_button(name, link, use_container_width=True)

                    st.divider()
                    st.markdown('<p class="section-header">📝 Summary</p>', unsafe_allow_html=True)
                    st.info(data["summary"])
                    st.markdown('<p class="section-header">🚀 Top Recommendation</p>', unsafe_allow_html=True)
                    st.warning(data["top_recommendation"])

                    st.divider()
                    st.markdown('<p class="section-header">📥 Download Report</p>', unsafe_allow_html=True)
                    pdf_buffer = generate_pdf_report(data, job_role, experience)
                    st.download_button(
                        label="📥 Download Full Report (PDF)",
                        data=pdf_buffer,
                        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"Error: {e}")


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
    jd_text = st.text_area(
        "Paste the Job Description here",
        height=200,
        placeholder="Paste the full job description here — skills required, experience, responsibilities..."
    )

    st.divider()
    st.markdown('<p class="section-header">📁 Upload Candidate Resumes (Max 5)</p>', unsafe_allow_html=True)
    uploaded_resumes = st.file_uploader(
        "Upload up to 5 resume PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_resumes:
        if len(uploaded_resumes) > 5:
            st.warning("⚠️ Maximum 5 resumes allowed. Only first 5 will be processed.")
            uploaded_resumes = uploaded_resumes[:5]
        st.success(f"✅ {len(uploaded_resumes)} resume(s) uploaded!")
        for f in uploaded_resumes:
            st.caption(f"📄 {f.name}")

    st.divider()
    if st.button("🔍 Screen Candidates", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please enter your API Key in the sidebar!")
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
                progress_bar.progress((i + 1) / len(uploaded_resumes),
                                      text=f"Analysing {candidate_name}...")
                try:
                    result = match_resume_to_jd(resume_text, candidate_name, jd_text, api_key)
                    results.append(result)
                except Exception as e:
                    st.error(f"Error analysing {candidate_name}: {e}")

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
                        for s in r["matched_skills"]:
                            st.success(s)
                    with dc2:
                        st.markdown("**❌ Missing Skills**")
                        for s in r["missing_skills"]:
                            st.warning(s)

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
