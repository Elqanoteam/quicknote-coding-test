# 📝 Notes Copilot - Coding Test

A coding test application that replicates our technical stack. This is a notes copilot that saves notes and uses AI to automatically generate summaries, topic tags, actionable follow-ups, and supports semantic search via embeddings.

## 🎯 Coding Test Instructions

**Welcome to the coding challenge!** This project contains **10 intentional bugs** that you need to find and fix. The bugs are more or less evenly distributed across:

- **Frontend (Vue.js)**
- **Backend (FastAPI)**
- **AI (Azure Openai)**

**Important Notes:**
- **Setup is NOT part of the test** - you should be able to set up and launch the application following the provided instructions
- If you encounter setup issues (e.g., dependency installation problems), these are not intentional bugs - please reach out for help
- We will provide you with the required Azure OpenAI endpoint and API key

Your task is to:
1. Clone the repository and set up the application following the instructions below
2. Identify and document each bug you find in the application logic/functionality
3. Fix all the bugs to make the application fully functional

The application should work end-to-end when all bugs are resolved. Good luck! 🚀

## ✨ Features

- **AI-Powered Analysis**: Automatic summary generation, topic tagging, and follow-up suggestions
- **Semantic Search**: Find notes by meaning, not just keywords
- **Task Management**: Track follow-up tasks with simple status toggling
- **Clean UI**: Modern Vue 3 interface with responsive design
- **Real-time**: Debounced search and live task updates

## 🛠 Tech Stack

- **Frontend**: Vue 3 + Vite
- **Backend**: Python FastAPI
- **AI**: Azure OpenAI GPT-4o-mini + text-embedding-ada-002

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Azure OpenAI API Endpoint & Key** (required for AI features)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone git@github.com:Elqanoteam/quicknote-coding-test.git
cd quicknote-coding-test
```

### 2. Environment Configuration

```bash
cp .env.example server/.env
```

Edit `server/.env` and add the Azure OpenAI credentials (provided separately):

```env
AZURE_OPENAI_ENDPOINT=<provided_by_elqano>
OPENAI_API_KEY=<provided_by_elqano>
```

### 3. Backend Setup

```bash
cd server
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Start Backend Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. Frontend Setup

```bash
cd ../web
npm install
npm run dev
```

The web app will be available at: http://localhost:5173

## 📖 Usage

### Creating Notes

1. Open the web app at http://localhost:5173
2. Fill in the title and content in the left panel
3. Click "Create Note"
4. The AI will automatically generate:
   - A concise summary (1-2 sentences)
   - 3-6 relevant topic tags
   - 3 actionable follow-up tasks

### Searching Notes

- Use the search bar in the right panel
- Search is semantic - it understands meaning, not just keywords
- Results are ranked by similarity and show match percentages
- Search is debounced (300ms) for smooth experience

### Managing Tasks

- View all tasks on the note detail page
- Click checkboxes to toggle between "open" and "done"
- Changes are saved immediately

### Navigation

- Click "View Details" on any note card to see the full note
- Use tags as clickable chips to search for related notes
- Use the back button to return to the main list

## 🔧 Configuration

All configuration is handled via environment variables in `server/.env`:

```env
# Required (provided by Elqano)
AZURE_OPENAI_ENDPOINT=<provided_by_elqano>
OPENAI_API_KEY=<provided_by_elqano>

# Optional (with defaults)
USE_AZURE_OPENAI=true
AZURE_OPENAI_API_VERSION=2024-08-01-preview
OPENAI_GEN_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-ada-002
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:5173
```

## 🧪 Testing

Run the test suite:

```bash
cd server
pytest tests
```

## 💰 Cost Considerations

**OpenAI API Usage:**
- Each note creation uses ~2-3 API calls (analysis + embedding)
- Searches only use embeddings API
- Using gpt-4o-mini and text-embedding-3-small for cost efficiency

**Tips to manage costs:**
- Keep note content concise (automatically truncated at 8000 characters)
- Monitor usage in OpenAI dashboard
- Consider implementing rate limiting for production use

## 🐛 Bug Hunting Tips

- **Test all features systematically** - create notes, search, manage tasks
- **Check browser console and network tabs** for frontend issues
- **Monitor backend logs** for API errors
- **Pay attention to edge cases** and error handling
- **Look for both functional and UX issues**
- **Remember: setup issues are NOT bugs** - focus on application functionality

## 📝 Submission Guidelines

### Getting Started
1. **Clone the repository** as your starting point
2. **Work on your own branch** or directly on main - your choice
3. **Make commits** as you fix each bug for better tracking

### When you've completed the test:
1. **Document each bug** you found (location, issue, fix)
2. **Ensure all features work end-to-end**
4. **Submit your changes as a git patch**

### Creating a Git Patch

After you've committed all your fixes, create a patch file:

```bash
# Create a patch with all your commits from the original state
git format-patch --stdout HEAD~<number_of_commits> > your-name-bugfixes.patch

# Or if you want all changes in one patch file:
git diff HEAD~<number_of_commits> > your-name-bugfixes.patch

# Or if you worked on a branch (recommended):
git checkout main
git format-patch main..your-branch-name --stdout > your-name-bugfixes.patch
```

**Example:**
```bash
# If you made 5 commits with fixes:
git format-patch --stdout HEAD~5 > yann-bugfixes.patch

# Or if you worked on a branch called "bugfixes":
git format-patch main..bugfixes --stdout > yann-bugfixes.patch
```

### What to Submit
- The `.patch` file containing all your changes
- A summary document listing each bug found and how you fixed it
- Any additional notes about your testing approach

---

**Happy bug hunting! 🐛🔍**
