# 🎯 SQL Practice Bot

An interactive SQL learning application powered by Claude AI, designed to help you prepare for data analytics and data engineering interviews.

## ✨ Features

- **AI-Generated Questions**: Get realistic, interview-style SQL questions tailored to your skill level
- **Dual Learning Tracks**:
  - Analytics/BI-focused SQL (aggregations, JOINs, window functions, metrics)
  - Data Engineer-focused SQL (schema design, ETL, transformations, SCD)
- **Three Difficulty Levels**: Beginner, Intermediate, Advanced
- **Multiple SQL Dialects**: PostgreSQL, MySQL, Snowflake, BigQuery
- **Instant AI Feedback**: Detailed grading with scores, feedback, and suggestions
- **Reference Solutions**: Learn from well-formatted solutions with explanations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd sql-test-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   The app will automatically open at `http://localhost:8501`

## 📖 How to Use

1. **Configure Your Session**
   - Select your learning track (Analytics or Data Engineer)
   - Choose difficulty level
   - Pick your preferred SQL dialect

2. **Generate Questions**
   - Click "Generate New Question" in the sidebar
   - Review the question and schema carefully

3. **Write Your Solution**
   - Type your SQL query in the text area
   - Click "Submit Answer" when ready

4. **Get Feedback**
   - Receive instant AI-powered grading (0-100 score)
   - Read detailed feedback on your approach
   - View reference solutions and explanations

## 🌐 Deploy to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Add your `ANTHROPIC_API_KEY` in Advanced Settings → Secrets
   - Click "Deploy"

3. **Configure Secrets** (in Streamlit Cloud dashboard)
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
   ```

## 📁 Project Structure

```
sql-test-bot/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── CLAUDE.md          # AI development documentation
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Claude 3.5 Haiku (Anthropic)
- **Language**: Python 3.8+
- **Key Libraries**:
  - `anthropic` - Claude API client
  - `streamlit` - Web UI framework
  - `python-dotenv` - Environment management

## 🎓 Learning Tracks

### Analytics/BI Track
Perfect for preparing for Business Intelligence, Analytics Engineer, or Data Analyst roles:
- Aggregate queries (GROUP BY, HAVING)
- Multi-table JOINs
- Window functions (ROW_NUMBER, RANK, LAG, LEAD)
- Business metrics (conversion rates, retention, cohorts)
- Date/time calculations

### Data Engineer Track
Ideal for Data Engineering and ETL Developer roles:
- Schema design and normalization
- Complex data transformations
- Slowly Changing Dimensions (SCD)
- Data quality and deduplication
- Partitioning strategies
- ETL pipeline logic

## 🔒 Security Notes

- Never commit your `.env` file (it's in `.gitignore`)
- Keep your API key secure and rotate it regularly
- For production deployments, use Streamlit Cloud secrets management

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

MIT License - feel free to use this for learning and teaching!

## 🙏 Acknowledgments

- Powered by [Anthropic's Claude](https://www.anthropic.com/)
- Built with [Streamlit](https://streamlit.io/)
- Inspired by real data analytics interview experiences

## 📧 Support

If you encounter issues:
1. Check that your API key is set correctly
2. Verify you have the latest dependencies installed
3. Review error messages in the Streamlit interface
4. Open an issue on GitHub with details

---

**Happy SQL practicing!** 🚀
