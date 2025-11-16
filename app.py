"""
SQL Practice Bot - Interactive SQL Learning Application

Setup:
1. Install dependencies: pip install -r requirements.txt
2. Set ANTHROPIC_API_KEY environment variable (or create .env file)
3. Run: streamlit run app.py

Environment Variables:
- ANTHROPIC_API_KEY: Your Anthropic API key (required)
"""

import os
import json
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
CLAUDE_MODEL = "claude-3-5-haiku-20241022"
MAX_TOKENS = 4096

# Tracks and difficulty levels
TRACKS = [
    "Analytics / BI-focused SQL",
    "Data Engineer-focused SQL"
]

DIFFICULTY_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

SQL_DIALECTS = [
    "PostgreSQL",
    "MySQL",
    "Snowflake",
    "BigQuery"
]


def get_claude_client():
    """
    Initialize and return the Anthropic client.
    Raises an error if ANTHROPIC_API_KEY is not set.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY environment variable not set. Please set it and restart the app.")
        st.stop()
    return Anthropic(api_key=api_key)


def generate_sql_question(track, difficulty, dialect):
    """
    Generate a SQL practice question using Claude API.

    Args:
        track (str): The learning track (Analytics or Data Engineer)
        difficulty (str): Question difficulty level
        dialect (str): SQL dialect to use

    Returns:
        dict: Question data containing:
            - question_text
            - schema_description
            - reference_sql
            - explanation
            - difficulty
            - track
    """
    client = get_claude_client()

    # Construct the prompt based on track
    track_guidance = ""
    if "Analytics" in track:
        track_guidance = """
        Focus on realistic interview-style SQL questions for Analytics/BI roles:
        - Aggregate queries with GROUP BY, HAVING
        - Multiple JOINs across tables
        - Window functions (ROW_NUMBER, RANK, LAG, LEAD, etc.)
        - Common BI metrics (conversion rates, retention, cohorts, running totals)
        - Date/time manipulations
        - Example domains: event analytics, e-commerce, product analytics, marketing metrics
        """
    else:
        track_guidance = """
        Focus on realistic interview-style SQL questions for Data Engineer roles:
        - Table design and schema reasoning
        - Complex joins and data transformations
        - Window functions for advanced analytics
        - Slowly changing dimensions (SCD Type 1, Type 2)
        - Data quality checks and deduplication
        - Partitioning concepts (conceptual understanding)
        - ETL-style data manipulation
        """

    difficulty_guidance = {
        "Beginner": "Keep it simple with 1-2 tables, basic JOINs, simple aggregations. No complex subqueries or window functions.",
        "Intermediate": "Use 2-3 tables, moderate complexity JOINs, window functions, CTEs, and subqueries are appropriate.",
        "Advanced": "Complex multi-table scenarios, advanced window functions, CTEs, complex business logic, edge cases."
    }

    system_prompt = f"""You are an expert SQL interview coach. Generate realistic SQL practice questions for data analytics roles.

{track_guidance}

Difficulty level: {difficulty}
{difficulty_guidance.get(difficulty, "")}

SQL Dialect: {dialect}

Guidelines:
- Create realistic, interview-style questions
- Keep schemas small (1-3 tables max)
- Provide clear table descriptions with sample data context
- Questions should test practical skills, not trivia
- Reference SQL should be production-quality code

Return ONLY a valid JSON object with this exact structure:
{{
    "question_text": "Clear problem statement here",
    "schema_description": "Table definitions and sample data context",
    "reference_sql": "Well-formatted SQL solution",
    "explanation": "Step-by-step explanation of the solution approach",
    "difficulty": "{difficulty}",
    "track": "{track}"
}}"""

    user_prompt = f"Generate a {difficulty.lower()} level SQL question for {track} using {dialect} syntax."

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract the response text
        response_text = response.content[0].text

        # Try to extract JSON from response (in case there's extra text)
        json_text = response_text.strip()

        # Find JSON object boundaries
        start_idx = json_text.find('{')
        end_idx = json_text.rfind('}')

        if start_idx != -1 and end_idx != -1:
            json_text = json_text[start_idx:end_idx + 1]

        # Parse JSON
        question_data = json.loads(json_text)

        # Validate required fields
        required_fields = ["question_text", "schema_description", "reference_sql", "explanation"]
        if not all(field in question_data for field in required_fields):
            raise ValueError("Missing required fields in Claude response")

        return question_data

    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse Claude response as JSON: {str(e)}")
        st.write("Raw response:", response_text if 'response_text' in locals() else "No response")
        return None
    except Exception as e:
        st.error(f"❌ Error generating question: {str(e)}")
        return None


def grade_sql_answer(question_text, schema_description, reference_sql, user_sql, difficulty, track):
    """
    Grade the user's SQL answer using Claude API.

    Args:
        question_text (str): The original question
        schema_description (str): Schema/table information
        reference_sql (str): The reference solution
        user_sql (str): The user's submitted SQL
        difficulty (str): Question difficulty level
        track (str): Learning track

    Returns:
        dict: Grading results containing:
            - score (int 0-100)
            - verdict (str)
            - feedback (str)
            - suggested_answer (str, optional)
    """
    client = get_claude_client()

    system_prompt = f"""You are an expert SQL instructor grading student solutions.

Evaluate the user's SQL answer against the reference solution. Consider:
- Correctness: Does it solve the problem?
- Completeness: Are all requirements addressed?
- Efficiency: Is the approach reasonable?
- Code quality: Readability, formatting, best practices
- Edge cases: Does it handle special scenarios?

Be constructive and educational. Point out both strengths and areas for improvement.

IMPORTANT: Return ONLY a valid JSON object. Use \\n for line breaks in feedback text, NOT actual newlines.

Return this exact structure:
{{
    "score": 85,
    "verdict": "Correct|Partially Correct|Incorrect",
    "feedback": "Detailed feedback here (2-3 paragraphs max). Use \\n for line breaks.",
    "suggested_answer": "Improved SQL if applicable (optional)"
}}

Score scale:
- 90-100: Excellent, correct and well-written
- 70-89: Good, mostly correct with minor issues
- 50-69: Partially correct, significant issues but on right track
- 0-49: Incorrect or fundamentally flawed approach"""

    user_prompt = f"""Question: {question_text}

Schema:
{schema_description}

Reference Solution:
```sql
{reference_sql}
```

User's Answer:
```sql
{user_sql}
```

Difficulty: {difficulty}
Track: {track}

Please grade the user's answer."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract response text
        response_text = response.content[0].text

        # Try to extract JSON from response (in case there's extra text)
        json_text = response_text.strip()

        # Find JSON object boundaries
        start_idx = json_text.find('{')
        end_idx = json_text.rfind('}')

        if start_idx != -1 and end_idx != -1:
            json_text = json_text[start_idx:end_idx + 1]

        # Parse JSON
        grading_data = json.loads(json_text)

        # Validate required fields
        required_fields = ["score", "verdict", "feedback"]
        if not all(field in grading_data for field in required_fields):
            raise ValueError("Missing required fields in Claude grading response")

        return grading_data

    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse grading response as JSON: {str(e)}")
        st.write("Raw response:", response_text if 'response_text' in locals() else "No response")
        return None
    except Exception as e:
        st.error(f"❌ Error grading answer: {str(e)}")
        return None


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'grading_result' not in st.session_state:
        st.session_state.grading_result = None
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = ""
    if 'track' not in st.session_state:
        st.session_state.track = TRACKS[0]
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = DIFFICULTY_LEVELS[0]
    if 'dialect' not in st.session_state:
        st.session_state.dialect = SQL_DIALECTS[0]


def render_sidebar():
    """Render the sidebar with configuration options."""
    st.sidebar.title("⚙️ Configuration")

    # Track selection
    st.session_state.track = st.sidebar.selectbox(
        "Track",
        TRACKS,
        index=TRACKS.index(st.session_state.track)
    )

    # Difficulty selection
    st.session_state.difficulty = st.sidebar.selectbox(
        "Difficulty",
        DIFFICULTY_LEVELS,
        index=DIFFICULTY_LEVELS.index(st.session_state.difficulty)
    )

    # SQL dialect selection
    st.session_state.dialect = st.sidebar.selectbox(
        "SQL Dialect",
        SQL_DIALECTS,
        index=SQL_DIALECTS.index(st.session_state.dialect)
    )

    st.sidebar.markdown("---")

    # Generate question button
    if st.sidebar.button("🎲 Generate New Question", type="primary", use_container_width=True):
        with st.spinner("Generating question..."):
            question_data = generate_sql_question(
                st.session_state.track,
                st.session_state.difficulty,
                st.session_state.dialect
            )

            if question_data:
                st.session_state.current_question = question_data
                st.session_state.grading_result = None
                st.session_state.user_answer = ""
                st.success("✅ New question generated!")
                st.rerun()

    # Information
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📚 How to Use
    1. Select your track and difficulty
    2. Generate a new question
    3. Write your SQL solution
    4. Submit for instant feedback

    ### 💡 Tips
    - Read the schema carefully
    - Test edge cases
    - Use proper formatting
    - Comment complex logic
    """)


def render_main_content():
    """Render the main content area with question and answer interface."""
    st.title("🎯 SQL Practice Bot")
    st.markdown("Practice SQL for your data analytics interview with AI-powered feedback")

    # Check if a question exists
    if st.session_state.current_question is None:
        st.info("👈 Get started by generating a question from the sidebar!")
        st.markdown("""
        ### Welcome to SQL Practice Bot!

        This app helps you prepare for data analytics interviews by:
        - **Generating** realistic SQL questions based on your skill level
        - **Evaluating** your solutions with detailed feedback
        - **Learning** from reference solutions and explanations

        Select your preferences in the sidebar and click "Generate New Question" to begin.
        """)
        return

    question = st.session_state.current_question

    # Display question metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Track", question.get('track', 'N/A'))
    with col2:
        st.metric("Difficulty", question.get('difficulty', 'N/A'))
    with col3:
        st.metric("Dialect", st.session_state.dialect)

    st.markdown("---")

    # Display question
    st.subheader("📋 Question")
    st.markdown(question['question_text'])

    # Display schema
    st.subheader("🗂️ Schema")
    st.code(question['schema_description'], language="sql")

    st.markdown("---")

    # Answer input
    st.subheader("✍️ Your Solution")
    user_answer = st.text_area(
        "Write your SQL query here:",
        value=st.session_state.user_answer,
        height=200,
        placeholder="SELECT ...",
        key="sql_input"
    )

    # Submit button
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("🚀 Submit Answer", type="primary", use_container_width=True)

    # Handle submission
    if submit_button:
        if not user_answer or user_answer.strip() == "":
            st.warning("⚠️ Please enter your SQL answer before submitting.")
        else:
            st.session_state.user_answer = user_answer

            with st.spinner("Grading your answer..."):
                grading_result = grade_sql_answer(
                    question['question_text'],
                    question['schema_description'],
                    question['reference_sql'],
                    user_answer,
                    question.get('difficulty', 'Intermediate'),
                    question.get('track', 'Analytics')
                )

                if grading_result:
                    st.session_state.grading_result = grading_result
                    st.rerun()

    # Display grading results if available
    if st.session_state.grading_result:
        st.markdown("---")
        render_grading_results()


def render_grading_results():
    """Render the grading results section."""
    result = st.session_state.grading_result
    question = st.session_state.current_question

    st.subheader("📊 Results")

    # Score and verdict
    col1, col2 = st.columns(2)
    with col1:
        score = result.get('score', 0)
        score_color = "normal"
        if score >= 90:
            score_emoji = "🌟"
        elif score >= 70:
            score_emoji = "✅"
        elif score >= 50:
            score_emoji = "⚠️"
        else:
            score_emoji = "❌"

        st.metric("Score", f"{score_emoji} {score}/100")

    with col2:
        verdict = result.get('verdict', 'Unknown')
        verdict_emoji = "✅" if verdict == "Correct" else "⚠️" if "Partial" in verdict else "❌"
        st.metric("Verdict", f"{verdict_emoji} {verdict}")

    # Feedback
    st.markdown("### 💬 Feedback")
    st.markdown(result.get('feedback', 'No feedback available'))

    # Suggested answer (if provided)
    if 'suggested_answer' in result and result['suggested_answer']:
        with st.expander("💡 Suggested Improvement"):
            st.code(result['suggested_answer'], language="sql")

    # Reference solution
    with st.expander("📖 Show Reference Solution & Explanation"):
        st.markdown("#### Reference SQL:")
        st.code(question['reference_sql'], language="sql")
        st.markdown("#### Explanation:")
        st.markdown(question['explanation'])


def main():
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(
        page_title="SQL Practice Bot",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # Render UI components
    render_sidebar()
    render_main_content()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
        "Powered by Claude AI | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
