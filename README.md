# 📝 Notes Copilot

A minimal but polished notes copilot that saves notes and uses AI to automatically generate summaries, topic tags, actionable follow-ups, and supports semantic search via embeddings.

## ✨ Features

- **AI-Powered Analysis**: Automatic summary generation, topic tagging, and follow-up suggestions
- **Semantic Search**: Find notes by meaning, not just keywords
- **Task Management**: Track follow-up tasks with simple status toggling
- **Clean UI**: Modern Vue 3 interface with responsive design
- **Real-time**: Debounced search and live task updates

## 🛠 Tech Stack

- **Frontend**: Vue 3 + Vite
- **Backend**: Python FastAPI
- **Database**: SQLite
- **AI**: OpenAI GPT-4o-mini + text-embedding-3-small

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key** (required for AI features)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd quicknotes-copilot
```

### 2. Environment Configuration

```bash
cp .env.example server/.env
```

Edit `server/.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
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
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (with defaults)
OPENAI_GEN_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:5173
```

## 🧪 Testing

Run the test suite:

```bash
cd server
pytest tests/ -v
```

The tests cover:
- Note creation with AI analysis
- Semantic search functionality
- API error handling
- Database operations

## 📊 API Endpoints

### Notes
- `POST /api/notes/` - Create a new note with AI analysis
- `GET /api/notes/` - List notes (with optional semantic search)
- `GET /api/notes/{id}` - Get a specific note

### Tasks
- `PATCH /api/tasks/{id}` - Update task status
- `GET /api/tasks/{id}` - Get a specific task

### Utility
- `GET /health` - Health check

## 🔒 Security Notes

- **API Key Security**: The OpenAI API key is never exposed to the frontend
- **CORS**: Configured to only allow requests from the Vite dev server
- **Input Validation**: All inputs are validated using Pydantic schemas
- **Error Handling**: Sensitive error details are not exposed to clients

## 💰 Cost Considerations

**OpenAI API Usage:**
- Each note creation uses ~2-3 API calls (analysis + embedding)
- Searches only use embeddings API
- Using gpt-4o-mini and text-embedding-3-small for cost efficiency

**Tips to manage costs:**
- Keep note content concise (automatically truncated at 8000 characters)
- Monitor usage in OpenAI dashboard
- Consider implementing rate limiting for production use

## 🐛 Troubleshooting

### Backend Issues

**"OpenAI API Key not found"**
- Ensure `OPENAI_API_KEY` is set in `server/.env`
- Restart the server after changing environment variables

**"Database connection failed"**
- Check that the `server/` directory is writable
- Delete `server/app.db` to reset the database

**"Module not found"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Frontend Issues

**"Cannot connect to backend"**
- Ensure backend server is running on port 8000
- Check CORS configuration in `server/.env`

**"Search not working"**
- Verify OpenAI API key has sufficient credits
- Check browser console for error messages

### Performance Issues

**Slow search results**
- Consider adding database indexes for large datasets
- Monitor OpenAI API response times

**High memory usage**
- Embeddings are stored in memory during search
- Consider implementing pagination for large note collections

## 🎯 Architecture Overview

### Backend (FastAPI)
```
server/
├── app/
│   ├── main.py          # FastAPI app and routes
│   ├── config.py        # Configuration management
│   ├── models.py        # SQLModel database models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── db.py           # Database connection
│   ├── ai.py           # OpenAI integration
│   ├── routers/        # API route modules
│   └── utils/          # Utility functions
└── tests/              # Test suite
```

### Frontend (Vue 3)
```
web/
├── src/
│   ├── main.js         # App entry point
│   ├── App.vue         # Root component
│   ├── api.js          # Backend API client
│   ├── styles.css      # Global styles
│   ├── components/     # Reusable components
│   └── pages/          # Route components
```

### Data Flow
1. **Note Creation**: User input → AI analysis → Database storage
2. **Semantic Search**: Query → Embedding → Similarity calculation → Results
3. **Task Updates**: UI interaction → API call → Database update

## 🚀 Deployment

### Backend Deployment
1. Set up Python environment on server
2. Configure environment variables
3. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend Deployment
1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Serve the `dist/` directory with a web server
3. Update API URLs in `src/api.js` for production

### Environment Variables for Production
```env
OPENAI_API_KEY=your_production_api_key
CORS_ORIGINS=https://your-frontend-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db  # For production DB
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the test files for example usage
3. Check the API documentation at http://localhost:8000/docs
4. Open an issue on the repository

---

**Happy note-taking! 📝✨**
