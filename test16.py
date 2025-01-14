import streamlit as st
st.set_page_config(
    page_title="EduChain Content Generator",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)

from educhain import Educhain, LLMConfig
import pandas as pd
import PyPDF2
from docx import Document
from langchain_openai import ChatOpenAI

# Set OpenAI API key directly
openai_api_key = "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"

# Initialize ChatOpenAI model
gpt_model = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key=openai_api_key
)

# Create LLMConfig with the custom model
gpt_config = LLMConfig(custom_model=gpt_model)

# Instantiate Educhain client with configuration
client = Educhain(config=gpt_config)

# Load quiz dataset
@st.cache_data
def load_quiz_dataset(file_path):
    try:
        return pd.read_csv(file_path)
    except pd.errors.ParserError as e:
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

quiz_dataset = load_quiz_dataset('quiz_dataset.csv')

# Streamlit app
st.title("EduChain: Content Generator & Quiz")

# Tab structure for the app
tab1, tab2, tab3 = st.tabs(["Generate Questions", "Take Quiz", "Lesson Plan"])

# Tab 1: Generate Questions
with tab1:
    st.header("Generate Questions")
    content_source = st.selectbox("Select Content Source", ["YouTube Video", "PDF", "Word Document", "URL", "Text File"])
    
    if content_source == "YouTube Video":
        video_url = st.text_input("Enter YouTube Video URL:")
    elif content_source in ["PDF", "Word Document", "Text File"]:
        uploaded_file = st.file_uploader(f"Upload a {content_source} File:", type=["pdf", "docx", "txt"])
    elif content_source == "URL":
        url = st.text_input("Enter URL:")
    
    if st.button("Generate Questions"):
        try:
            questions = []
            if content_source == "YouTube Video" and video_url:
                questions = client.qna_engine.generate_questions_from_youtube(video_url, num=3)
            elif content_source in ["PDF", "Word Document", "Text File"] and uploaded_file:
                if uploaded_file is not None:
                    uploaded_file.seek(0)  # Reset file pointer to the beginning
                    questions = client.qna_engine.generate_questions_from_data(
                        source=uploaded_file.read(), source_type=content_source.lower(), num=3
                    )
            elif content_source == "URL" and url:
                questions = client.qna_engine.generate_questions_from_data(url, source_type="url", num=3)
            else:
                st.warning("Please provide valid input!")
            
            if questions:
                st.session_state.questions = questions.json()
                st.success("Questions Generated!")
                st.write("## Generated Questions:")
                for q in questions.json():
                    st.write(f"**Q:** {q['question']}")
                    for option in q['options']:
                        st.write(f"- {option}")
        except Exception as e:
            st.error(f"Error: {e}")

# Tab 2: Take Quiz
with tab2:
    st.header("Quiz")
    if "questions" in st.session_state and st.session_state.questions:
        quiz_results = {}
        for q in st.session_state.questions:
            answer = st.radio(q['question'], q['options'])
            quiz_results[q['question']] = answer
        
        if st.button("Submit Quiz"):
            # Example logic for analyzing quiz results
            areas_of_improvement = ["Topic 1", "Topic 2"]  # Replace with actual analysis logic
            st.write("### Areas of Improvement:")
            st.write(areas_of_improvement)
    else:
        st.warning("No questions available. Please generate questions first.")

# Tab 3: Lesson Plan
with tab3:
    st.header("Lesson Plan")
    topic = st.text_input("Enter Lesson Topic:")
    duration = st.text_input("Enter Lesson Duration (e.g., 60 minutes):", value="60 minutes")
    grade_level = st.text_input("Enter Grade Level (e.g., High School):", value="High School")
    learning_objectives = st.text_area("Enter Learning Objectives (comma-separated):", value="")

    if st.button("Generate Lesson Plan"):
        try:
            lesson_plan = client.content_engine.generate_lesson_plan(
                topic=topic,
                duration=duration,
                grade_level=grade_level,
                learning_objectives=learning_objectives.split(",") if learning_objectives else []
            )
            st.write("### Generated Lesson Plan:")
            st.json(lesson_plan.json())
        except Exception as e:
            st.error(f"Error: {e}")

# General app setup
st.sidebar.info("Use the tabs above to navigate through the application.")
st.sidebar.markdown("""
    - **Generate Questions**: Input content from different sources to generate quiz questions.
    - **Take Quiz**: Answer the generated quiz questions.
    - **Lesson Plan**: Create a lesson plan based on user input or quiz analysis.
""")

# Function to analyze quiz results
def analyze_quiz_results(quiz_results):
    # Placeholder logic to analyze quiz results and identify areas of improvement
    areas_of_improvement = ["Topic 1", "Topic 2"]
    return areas_of_improvement

# Function to generate lesson plan based on areas of improvement
def generate_lesson_plan(areas_of_improvement):
    lesson_plan = "Lesson Plan:\n"
    for topic in areas_of_improvement:
        lesson_plan += f"- Review {topic}\n"
    return lesson_plan

# # Run the Streamlit app
# if __name__ == "__main__":
#     st.set_page_config(page_title="EduChain Content Generator", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
