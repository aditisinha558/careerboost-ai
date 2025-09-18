
import streamlit as st
from resume_utils import extract_text_from_pdf_bytes, match_keywords, suggest_action_words, readability_score, overall_score, rewrite_resume_text, extract_keywords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io, datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="CareerBoost AI", layout="wide")
st.set_page_config(page_title="CareerBoost AI", layout="wide")

# Title & Supporting Line
st.title("🚀 CareerBoost AI — Resume & Cover Letter Optimizer")
st.markdown(
    """
    **Turn your resume, job description, and cover letter into a perfect match in seconds.**  
    ATS-friendly, skill-focused, and designed to get you noticed by recruiters.
    """,
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("About CareerBoost AI")
    st.write(
        "CareerBoost AI helps job seekers instantly tailor their resumes and cover letters "
        "to any job description. Perfect for building a portfolio, preparing for interviews, "
        "and boosting recruiter visibility."
    )
    st.markdown("---")
    st.info("💡 **Tip:** Use a real job description from your target role. Add relevant keywords into your resume headline and skills section for the best results.")
    st.caption("Made with ❤️ by Aditi Sinha | Connect on [LinkedIn](www.linkedin.com/in/aditi-sinha-0225b7168)")

col1, col2 = st.columns([1,2])

with col1:
    st.subheader("Input")
    name = st.text_input("Your full name", value="John Doe")
    company = st.text_input("Target company", value="Company")
    position = st.text_input("Target position", value="Software Engineer")
    uploaded_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])
    resume_text_area = st.text_area("Or paste resume text (optional)", height=200)
    job_text = st.text_area("Paste job description", height=250)
    analyze = st.button("Analyze")

with col2:
    if analyze:
        # get resume text
        if uploaded_file:
            resume_bytes = uploaded_file.read()
            resume_text = extract_text_from_pdf_bytes(resume_bytes)
        else:
            resume_text = resume_text_area

        if not resume_text or not job_text:
            st.error("Please provide both a resume and a job description.")
        else:
            # Keyword matching
            keyword_score, matched, missing = match_keywords(resume_text, job_text)
            # Readability
            read_score = readability_score(resume_text)
            total = overall_score(keyword_score, read_score)
            # Action words
            suggestions = suggest_action_words(resume_text)
            # Rewrite resume suggestion
            optimized_text = rewrite_resume_text(resume_text, matched, missing)
            # Cover letter
            kw = ", ".join(matched[:6]) if matched else "relevant skills"
            cover_letter = f"""
            Dear Hiring Manager at {company},

            I am excited to apply for the {position} role at {company}. After reviewing your job description, I believe my skills and background align closely with your requirements.

            In my experience, I have successfully worked with {kw}, which I believe would help me make a meaningful contribution to {company}'s goals. I am confident in my ability to plan, execute, and optimize initiatives that drive measurable results, while collaborating closely with cross-functional teams.

            I am passionate about bringing creativity, data-driven decision making, and continuous improvement to every project I take on. I would welcome the opportunity to discuss how my skills can support {company}'s growth and success.

            Thank you for considering my application.

            Sincerely,  
            {name}
            """

            # Display scores
            st.metric("Overall score", f"{total}%")
            st.write("Breakdown:")
            c1, c2, c3 = st.columns(3)
            c1.metric("Keyword match", f"{keyword_score}%")
            c2.metric("Readability", f"{read_score}%")
            c3.metric("Missing keywords", len(missing))

            # Charts: bar chart
            fig, ax = plt.subplots(figsize=(4,2.5))
            ax.bar(["Keywords","Readability"], [keyword_score, read_score], color=["#4f46e5","#06b6d4"])
            ax.set_ylim(0,100)
            ax.set_ylabel("Score (%)")
            st.pyplot(fig, clear_figure=True)

            # Wordcloud for job keywords
            job_kws = list(extract_keywords(job_text))
            if job_kws:
                wc = WordCloud(width=600, height=300, background_color="white").generate(" ".join(job_kws))
                fig2, ax2 = plt.subplots(figsize=(6,3))
                ax2.imshow(wc, interpolation="bilinear")
                ax2.axis("off")
                st.pyplot(fig2, clear_figure=True)

            st.subheader("Matched keywords")
            if matched:
                st.write(", ".join(matched))
            else:
                st.info("No matched keywords found. Consider adding role-specific skills.")

            st.subheader("Skill gap / Missing keywords (top 20)")
            if missing:
                st.write(", ".join(missing[:20]))
            else:
                st.write("No major missing keywords detected.")

            st.subheader("Action-word suggestions (weak → strong)")
            if suggestions:
                for k,v in suggestions.items():
                    st.write(f"**{k}** → {v}")
            else:
                st.write("No weak verbs detected.")

            st.subheader("Suggested (optimized) resume text preview")
            st.code(optimized_text[:3000])

            st.subheader("Suggested cover letter")
            st.code(cover_letter)

            # Download optimized resume (text file)
            ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            st.download_button("Download optimized resume (.txt)", data=optimized_text, file_name=f"careerboost_optimized_{ts}.txt", mime="text/plain")

            # Create and download PDF report
            def make_pdf(name, company, position, total, keyword_score, read_score, matched, missing, suggestions, cover_letter):
                buf = io.BytesIO()
                p = canvas.Canvas(buf, pagesize=letter)
                width, height = letter
                p.setFont("Helvetica-Bold", 16)
                p.drawString(50, height - 50, "CareerBoost AI - Analysis Report")
                p.setFont("Helvetica", 12)
                p.drawString(50, height - 80, f"Name: {name}")
                p.drawString(50, height - 100, f"Position: {position} at {company}")
                p.drawString(50, height - 120, f"Overall Score: {total}%")
                p.drawString(50, height - 140, f"Keyword Match: {keyword_score}%  |  Readability: {read_score}%")
                y = height - 170
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, "Matched Keywords:")
                p.setFont("Helvetica", 11)
                y -= 18
                for kw in matched:
                    p.drawString(60, y, f"- {kw}")
                    y -= 14
                    if y < 80:
                        p.showPage(); y = height - 50
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, "Missing Keywords (Skill Gap):")
                y -= 18
                p.setFont("Helvetica", 11)
                for kw in missing:
                    p.drawString(60, y, f"- {kw}")
                    y -= 14
                    if y < 80:
                        p.showPage(); y = height - 50
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, "Action Word Suggestions:")
                y -= 18
                p.setFont("Helvetica", 11)
                for k,v in suggestions.items():
                    p.drawString(60, y, f"- {k} -> {v}")
                    y -= 14
                    if y < 80:
                        p.showPage(); y = height - 50
                p.showPage()
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, height - 50, "Suggested Cover Letter:")
                p.setFont("Helvetica", 11)
                textobj = p.beginText(50, height - 80)
                for line in cover_letter.splitlines():
                    textobj.textLine(line)
                p.drawText(textobj)
                p.save()
                buf.seek(0)
                return buf
            pdf_buf = make_pdf(name, company, position, total, keyword_score, read_score, matched, missing, suggestions, cover_letter)
            st.download_button("Download full PDF report", data=pdf_buf, file_name=f"careerboost_report_{ts}.pdf", mime="application/pdf")

            # small CTA
            st.markdown("---")
            st.info("Tip: For best results, add matched keywords to your resume headline and skills section.")
