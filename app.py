import streamlit as st
import pandas as pd
import spacy
from utils.parser import extract_text_from_pdf, extract_fields
from utils.storage import save_data, load_all_data


st.set_page_config(page_title="Resume Skill Extractor", layout="wide", initial_sidebar_state="expanded")

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/942/942748.png",
    width=100,
)
st.sidebar.title("Resume Skill Extractor")
st.sidebar.markdown(
    """
    - Upload PDF resumes and extract key info.
    - Filter/search resumes by skills, name, or experience.
    - Analyze your talent pool!
    - Download results as CSV or JSON.
    """
)
st.sidebar.markdown("---")


openai_api_key = "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"  # use your secret or input

nlp = spacy.load("en_core_web_sm")

st.markdown(
    "<h1 style='text-align: center; color: #0066cc;'>📄 Resume Skill Extractor</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: gray;'>Fast, smart, and simple PDF resume parsing with instant analytics.</p>",
    unsafe_allow_html=True,
)

st.subheader("Step 1: Upload a Resume PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", help="Upload a PDF resume to extract details.")

if uploaded_file and openai_api_key:
    with st.spinner("Extracting... This can take a few seconds."):
        text = extract_text_from_pdf(uploaded_file)
        if text:
            name, email, phone, skills, experience = extract_fields(
                text, nlp, openai_api_key=openai_api_key
            )
            skill_tags = [f"<span style='background-color:#d1e7dd; color:#155724; border-radius:4px; padding:3px 7px; margin-right:4px;'>{sk}</span>"
                          for sk in skills] if skills else ["<i>No primary skills found</i>"]
            st.markdown("#### Extracted Resume Summary")
            st.markdown(f"**Name:** <span style='color:#00509e'>{name or 'Not found'}</span>", unsafe_allow_html=True)
            st.markdown(f"**Email:** {email or '<i>Not found</i>'}", unsafe_allow_html=True)
            st.markdown(f"**Phone:** {phone or '<i>Not found</i>'}", unsafe_allow_html=True)
            st.markdown("**Skills:** " + " ".join(skill_tags), unsafe_allow_html=True)
            st.markdown("**Work Experience:**")
            if experience:
                for exp in experience:
                    st.markdown(f"<li>{exp}</li>", unsafe_allow_html=True)
            else:
                st.write("_No detailed work experience detected._")
            if st.button("💾 Save to Database"):
                save_data({
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "skills": skills,
                    "experience": experience
                })
                st.success("Saved Successfully!")
elif uploaded_file and not openai_api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to extract skills and experience.")

st.markdown("---")

# --- Load and Display All Data ---
st.subheader("Step 2: Browse & Filter Stored Resumes")
data = load_all_data()
if data:
    df = pd.DataFrame(data)
    df["skills_str"] = df["skills"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")

    st.markdown("##### Search & Filter")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        search_name = st.text_input("Filter by Name")
    with col2:
        search_skill = st.text_input("Filter by Primary Skill (e.g., Python, Java)")
    with col3:
        min_exp = st.number_input("Min. Work Experience Entries", 0, 10, 0)

    filtered = df
    if search_name:
        filtered = filtered[filtered["name"].str.contains(search_name, case=False, na=False)]
    if search_skill:
        filtered = filtered[filtered["skills_str"].str.contains(search_skill, case=False, na=False)]
    if min_exp > 0:
        filtered = filtered[filtered["experience"].apply(lambda x: len(x) if isinstance(x, list) else 0) >= min_exp]

    def highlight_skills(skill_list):
        if not skill_list:
            return ""
        return " ".join(
            [f"<span style='background-color:#d1e7dd; color:#155724; border-radius:4px; padding:2px 6px;'>{sk}</span>"
             for sk in skill_list]
        )

    filtered["skills_highlighted"] = filtered["skills"].apply(highlight_skills)
    filtered["experience_preview"] = filtered["experience"].apply(
        lambda x: "<br>".join(x[:2]) + (" ..." if len(x) > 2 else "") if isinstance(x, list) else ""
    )
    

    st.write(f"Showing {len(filtered)} of {len(df)} resumes")

    st.write(
        filtered[["name", "email", "phone", "skills_highlighted", "experience_preview"]]
        .rename(columns={"skills_highlighted": "Primary Skills", "experience_preview": "Work Experience"})
        .to_html(escape=False, index=False), unsafe_allow_html=True
    )

    st.markdown("#### Download Extracted Data")
    colcsv, coljson = st.columns(2)
    with colcsv:
        csv = filtered.drop(columns=["skills_highlighted", "experience_preview"]).to_csv(index=False).encode()
        st.download_button("⬇️ Download as CSV", csv, "resumes.csv", "text/csv")
    with coljson:
        json_str = filtered.drop(columns=["skills_highlighted", "experience_preview"]).to_json(orient="records", indent=2)
        st.download_button("⬇️ Download as JSON", json_str, "resumes.json", "application/json")

    st.markdown("---")

    # --- Resume Analytics/Dashboard ---
    st.subheader("Step 3: Resume Analytics Dashboard")
    st.markdown("_Visualize the distribution of primary skills and detailed experience entries across your resumes._")
    skill_count = pd.Series([sk for sublist in filtered["skills"] for sk in (sublist if isinstance(sublist, list) else [])]).value_counts()
    exp_counts = filtered["experience"].apply(lambda x: len(x) if isinstance(x, list) else 0)

    st.bar_chart(skill_count)  # Complete bar chart for all primary skills
else:
    st.info("No resumes stored yet. Upload one to get started!")

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("Resume Skill Extractor Demo | UI/UX enhanced for Codeium Assignment")