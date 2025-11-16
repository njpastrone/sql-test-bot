# 🤖 Claude AI Integration Documentation

This document details how Claude AI is integrated into the SQL Practice Bot, including prompt engineering strategies, model configuration, and best practices.

## 🧠 AI Architecture

### Model Selection

**Current Model**: Claude 3.5 Haiku (`claude-3-5-haiku-20241022`)

**Why Haiku?**
- **Speed**: Fast response times for real-time grading feedback
- **Cost-Effective**: Lower token costs for educational applications
- **Quality**: Excellent at structured outputs (JSON) and SQL reasoning
- **Context Window**: 200K tokens (more than sufficient for SQL questions)

### Alternative Models
```python
# In app.py, line 23:
CLAUDE_MODEL = "claude-3-5-haiku-20241022"  # Current (fast, cheap)
# CLAUDE_MODEL = "claude-3-5-sonnet-20240620"  # Higher quality, slower
# CLAUDE_MODEL = "claude-3-opus-20240229"  # Best quality, expensive
```

## 📝 Prompt Engineering

### 1. Question Generation Prompt

**Location**: `generate_sql_question()` function

**Key Techniques**:
- **Role Assignment**: "You are an expert SQL interview coach"
- **Structured Output**: Enforces strict JSON format
- **Context-Specific Guidance**: Different prompts for Analytics vs Data Engineer tracks
- **Difficulty Calibration**: Explicit instructions for Beginner/Intermediate/Advanced
- **Realism Focus**: Emphasizes interview-style questions over academic problems

**Example Track-Specific Guidance**:

```python
# Analytics Track
track_guidance = """
Focus on realistic interview-style SQL questions for Analytics/BI roles:
- Aggregate queries with GROUP BY, HAVING
- Multiple JOINs across tables
- Window functions (ROW_NUMBER, RANK, LAG, LEAD, etc.)
- Common BI metrics (conversion rates, retention, cohorts, running totals)
- Date/time manipulations
- Example domains: event analytics, e-commerce, product analytics, marketing metrics
"""

# Data Engineer Track
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
```

**Output Schema**:
```json
{
    "question_text": "Clear problem statement",
    "schema_description": "Table definitions and sample data context",
    "reference_sql": "Well-formatted SQL solution",
    "explanation": "Step-by-step explanation",
    "difficulty": "Beginner|Intermediate|Advanced",
    "track": "Analytics / BI-focused SQL"
}
```

### 2. Answer Grading Prompt

**Location**: `grade_sql_answer()` function

**Key Techniques**:
- **Evaluation Criteria**: Explicit rubric (correctness, completeness, efficiency, code quality, edge cases)
- **Constructive Feedback**: Emphasizes educational value
- **Scoring Scale**: Clear 0-100 scale with guidelines
- **Structured Feedback**: JSON output for consistent parsing
- **Comparative Analysis**: User answer vs reference solution

**Grading Rubric**:
```
- 90-100: Excellent, correct and well-written
- 70-89: Good, mostly correct with minor issues
- 50-69: Partially correct, significant issues but on right track
- 0-49: Incorrect or fundamentally flawed approach
```

**Output Schema**:
```json
{
    "score": 85,
    "verdict": "Correct|Partially Correct|Incorrect",
    "feedback": "Detailed feedback (2-3 paragraphs)",
    "suggested_answer": "Improved SQL (optional)"
}
```

## 🔧 Technical Implementation

### JSON Parsing Strategy

**Challenge**: Claude sometimes returns valid JSON with control characters or extra text.

**Solution**: Robust extraction logic
```python
# Extract JSON from response
json_text = response_text.strip()
start_idx = json_text.find('{')
end_idx = json_text.rfind('}')

if start_idx != -1 and end_idx != -1:
    json_text = json_text[start_idx:end_idx + 1]

grading_data = json.loads(json_text)
```

### Error Handling

**Three-Layer Approach**:
1. **API Key Validation**: Check environment variable on startup
2. **JSON Parsing**: Try/except with user-friendly error messages
3. **Field Validation**: Ensure all required fields present

```python
try:
    # API call
    response = client.messages.create(...)

    # JSON extraction & parsing
    question_data = json.loads(json_text)

    # Validation
    required_fields = ["question_text", "schema_description", ...]
    if not all(field in question_data for field in required_fields):
        raise ValueError("Missing required fields")

except json.JSONDecodeError as e:
    st.error(f"Failed to parse: {str(e)}")
    st.write("Raw response:", response_text)
except Exception as e:
    st.error(f"Error: {str(e)}")
```

## 🎯 Prompt Optimization Tips

### For Better Question Generation

1. **Increase Difficulty Gradually**: Start with beginner to understand the pattern
2. **Specify Domain**: Add domain preferences in system prompt (e.g., "focus on e-commerce analytics")
3. **Control Complexity**: Adjust max table count or query features
4. **Dialect Specificity**: Emphasize dialect-specific features (e.g., "use Snowflake's QUALIFY clause")

### For Better Grading

1. **Add Examples**: Include example good/bad answers in system prompt
2. **Rubric Details**: Expand evaluation criteria for specific aspects
3. **Tone Control**: Adjust feedback tone (encouraging vs strict)
4. **Partial Credit**: Fine-tune scoring for partially correct solutions

## 📊 Token Usage

### Typical Usage Per Session

| Action | Input Tokens | Output Tokens | Approx Cost (Haiku) |
|--------|--------------|---------------|---------------------|
| Generate Question | ~500 | ~400 | $0.0001 |
| Grade Answer | ~800 | ~300 | $0.0002 |
| **Per Question Cycle** | **~1,300** | **~700** | **~$0.0003** |

**Note**: Costs are approximate based on Anthropic's pricing for Claude 3.5 Haiku.

### Cost Optimization

Current settings:
```python
MAX_TOKENS = 4096  # Maximum tokens for response
```

For production:
- Monitor actual token usage via API responses
- Adjust MAX_TOKENS if responses are consistently shorter
- Consider caching common questions (not implemented)

## 🔄 Future Enhancements

### Potential Improvements

1. **Multi-Turn Conversations**
   - Allow users to ask follow-up questions about feedback
   - Implement conversation history in session state

2. **Advanced Prompt Chaining**
   - First pass: Generate question outline
   - Second pass: Expand with schema and solution
   - Results in more consistent quality

3. **Few-Shot Learning**
   - Include example questions in system prompt
   - Demonstrate desired format and style

4. **Dynamic Difficulty Adjustment**
   - Track user performance over session
   - Auto-adjust difficulty based on success rate

5. **Specialized Grading**
   - Performance analysis (explain plan-level feedback)
   - Security checks (SQL injection patterns)
   - Style guide enforcement

## 🧪 Testing Prompts

### Test Question Generation
```python
# In Python console or notebook:
from app import generate_sql_question

result = generate_sql_question(
    track="Analytics / BI-focused SQL",
    difficulty="Intermediate",
    dialect="PostgreSQL"
)

print(result['question_text'])
print(result['reference_sql'])
```

### Test Grading
```python
from app import grade_sql_answer

result = grade_sql_answer(
    question_text="Calculate total sales by region",
    schema_description="sales(id, region, amount)",
    reference_sql="SELECT region, SUM(amount) FROM sales GROUP BY region",
    user_sql="SELECT region, SUM(amount) FROM sales GROUP BY region",
    difficulty="Beginner",
    track="Analytics"
)

print(f"Score: {result['score']}")
print(f"Feedback: {result['feedback']}")
```

## 📚 Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🔐 Security Considerations

1. **API Key Management**
   - Never hardcode API keys
   - Use environment variables or Streamlit secrets
   - Rotate keys regularly

2. **Input Validation**
   - User SQL is sent to Claude (read-only analysis)
   - No actual SQL execution on databases
   - Safe for untrusted user input

3. **Rate Limiting**
   - Consider implementing rate limits for production
   - Monitor API usage to prevent abuse

---

**Last Updated**: 2025-11-16
**Claude Model**: Claude 3.5 Haiku (claude-3-5-haiku-20241022)
