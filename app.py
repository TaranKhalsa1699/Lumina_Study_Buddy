import streamlit as st
import os
from dotenv import load_dotenv
from utils import (
    get_groq_client, extract_text_from_pdf, generate_summary, 
    explain_topic, generate_quiz, generate_flashcards
)

# Page Config
st.set_page_config(page_title="Lumina | AI Study Buddy", page_icon="🎓", layout="wide")

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🎓 Lumina AI")
    st.markdown("---")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.info("Get your key from [console.groq.com](https://console.groq.com/keys)")
    
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📝 Notes Summarizer", "🧠 Concept Explainer", "📝 Quiz Master", "🃏 Flashcards"]
    )
    st.markdown("---")
    st.success("Level up your learning!")

# Check for API Key
if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar to start.")
    st.stop()

client = get_groq_client(api_key)

# App Logic
if menu == "🏠 Dashboard":
    st.title("Welcome back, Scholar! ✨")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>Ready to Ace your Exams?</h3>
            <p>Lumina is your personal AI tutor designed to make studying efficient and fun.</p>
            <ul>
                <li><b>Summarize</b> long PDF notes instantly</li>
                <li><b>Clarify</b> tough concepts with ELI5</li>
                <li><b>Test</b> yourself with AI-generated quizzes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.image("https://img.freepik.com/free-vector/learning-concept-illustration_114360-6186.jpg")

elif menu == "📝 Notes Summarizer":
    st.title("📝 Notes Summarizer")
    uploaded_file = st.file_uploader("Upload your lecture notes (PDF)", type="pdf")
    
    if uploaded_file:
        if st.button("Generate Summary"):
            with st.spinner("Lumina is reading your notes..."):
                text = extract_text_from_pdf(uploaded_file)
                summary = generate_summary(client, text)
                st.markdown("### Summary")
                st.markdown(summary)
                st.download_button("Download Summary", summary, file_name="summary.txt")

elif menu == "🧠 Concept Explainer":
    st.title("🧠 Concept Explainer")
    topic = st.text_input("What concept is confusing you?")
    level = st.select_slider("Select depth of explanation", options=["Beginner (ELI5)", "Intermediate", "Advanced"])
    
    if st.button("Explain to me"):
        with st.spinner(f"Simplifying {topic}..."):
            explanation = explain_topic(client, topic, level)
            st.markdown(f"### {topic}")
            st.markdown(explanation)

elif menu == "📝 Quiz Master":
    st.title("📝 Quiz Master")
    uploaded_file = st.file_uploader("Upload notes to generate a quiz (PDF)", type="pdf")
    
    if uploaded_file:
        if st.button("Generate Quiz"):
            with st.spinner("Creating your custom quiz..."):
                text = extract_text_from_pdf(uploaded_file)
                quiz_data = generate_quiz(client, text)
                st.session_state.quiz = quiz_data
                st.session_state.answers = {}

    if 'quiz' in st.session_state:
        for i, q in enumerate(st.session_state.quiz):
            st.subheader(f"Q{i+1}: {q['question']}")
            ans = st.radio(f"Select option for Q{i+1}", q['options'], key=f"q_{i}")
            st.session_state.answers[i] = ans
            
        if st.button("Submit Quiz"):
            score = 0
            for i, q in enumerate(st.session_state.quiz):
                if st.session_state.answers.get(i) == q['answer']:
                    score += 1
            st.success(f"Your Score: {score}/{len(st.session_state.quiz)}")

elif menu == "🃏 Flashcards":
    st.title("🃏 Flashcards Generator")
    uploaded_file = st.file_uploader("Upload notes for flashcards (PDF)", type="pdf")
    
    if uploaded_file:
        if st.button("Create Flashcards"):
            with st.spinner("Extracting key terms..."):
                text = extract_text_from_pdf(uploaded_file)
                cards = generate_flashcards(client, text)
                st.session_state.cards = cards

    if 'cards' in st.session_state:
        cols = st.columns(2)
        for i, card in enumerate(st.session_state.cards):
            with cols[i % 2]:
                with st.expander(f"🎴 Card {i+1}: {card['front']}"):
                    st.info(card['back'])

st.markdown("---")
st.caption("Powered by Groq & Streamlit | Built for Students")
