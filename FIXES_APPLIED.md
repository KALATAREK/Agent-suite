# AgentSuite - Project Setup & Running Guide

## ✅ Project Status: FIXED AND RUNNING

Your AgentSuite project has been completely fixed and is now running successfully!

## 📋 Fixes Applied

### 1. **Backend Python Dependencies** ✅
- **File**: `backend/requirements.txt`
- **Issue**: Missing critical dependencies (passlib, version pinning)
- **Fix**: Added complete pinned dependencies including:
  - FastAPI 0.104.1
  - Uvicorn 0.24.0
  - SQLAlchemy 2.0.23
  - Pydantic 2.4.2
  - python-jose with cryptography
  - passlib for password hashing
  - Google Auth, OpenAI, and other required packages

### 2. **Frontend Environment Configuration** ✅
- **File**: `frontend/.env.local`
- **Issue**: Missing API URL configuration
- **Fix**: Added `NEXT_PUBLIC_API_URL=http://localhost:8000`

### 3. **Component Import Paths** ✅
- **File**: `frontend/app/page.tsx`
- **Issue**: Case-sensitive imports using lowercase paths
- **Fix**: Corrected imports to use proper casing:
  - `@/components/sidebar` → `@/components/Sidebar`
  - `@/components/topbar` → `@/components/Topbar`

### 4. **API URL Integration** ✅
- **File**: `frontend/lib/api.ts`
- **Issue**: Hardcoded API URL
- **Fix**: Now uses environment variable with fallback

### 5. **Topbar Component API Integration** ✅
- **File**: `frontend/components/Topbar.tsx`
- **Issue**: Hardcoded API URL and duplicated auth logic
- **Fix**: Refactored to use `apiFetch` utility for consistency

---

## 🚀 Running the Project

### **Option 1: Individual Terminal Sessions (Recommended for Development)**

#### Terminal 1 - Backend Server:
```powershell
cd c:\Users\Palus\Documents\agentsuite
& .\.venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Terminal 2 - Frontend Server:
```powershell
cd c:\Users\Palus\Documents\agentsuite\frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.2.2 (Turbopack)
- Local:         http://localhost:3000
✓ Ready in 568ms
```

### **Option 2: Using npm scripts from root (Future Enhancement)**

Create a root `Makefile` or `package.json` with concurrent scripts:
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && uvicorn main:app --reload",
    "dev:frontend": "cd frontend && npm run dev"
  }
}
```

---

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 🔐 Authentication Flow

1. Navigate to http://localhost:3000/login
2. Options:
   - **Register**: Create account with email/password
   - **Login**: Sign in with existing credentials
   - **Google Auth**: Click "Sign in with Google"

3. After successful authentication:
   - JWT token saved to localStorage
   - Redirected to main dashboard
   - Can access Assistant, Analyzer, and Automator features

---

## 🧪 Testing the API

### Test Backend Health:
```bash
curl http://localhost:8000/
```

### Register User:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

---

## 📦 Project Structure

```
agentsuite/
├── backend/
│   ├── main.py                 # FastAPI app with all routes
│   ├── database.py             # SQLite setup
│   ├── requirements.txt        # Python dependencies ✅ FIXED
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy models
│   │   ├── request_models.py   # Pydantic request schemas
│   │   ├── response_models.py  # Response schemas
│   │   └── memory_models.py
│   ├── agents/                 # AI agent logic
│   ├── services/               # Business logic services
│   ├── routes/                 # API route handlers
│   └── prompts/                # LLM prompts
│
├── frontend/
│   ├── .env.local              # Environment config ✅ FIXED
│   ├── app/
│   │   ├── layout.tsx          # Root layout with styling
│   │   ├── page.tsx            # Main dashboard ✅ FIXED IMPORTS
│   │   └── login/
│   │       └── page.tsx        # Authentication page
│   ├── components/             # React components ✅ FIXED IMPORTS
│   ├── lib/
│   │   └── api.ts              # API client utility ✅ FIXED
│   └── package.json
```

---

## 🔧 Database

- **Type**: SQLite (default)
- **File**: `backend/agentsuite.db`
- **Tables**: Users, Sessions, Messages
- **Auto-Migration**: Database tables created on first run

### Reset Database:
```bash
cd backend
rm agentsuite.db
# Next run will recreate it
```

---

## 🔑 Environment Variables

### Backend (`.env`):
```
OPENAI_API_KEY=your_key_here
GOOGLE_CLIENT_ID=your_client_id
JWT_SECRET_KEY=your_secret_key
```

### Frontend (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id
```

---

## ⚙️ Available Features

### 1. **Assistant Agent** 💬
- Real-time chat interface
- Conversation memory
- Auto-naming sessions
- Message history

### 2. **Analyzer Agent** 📊
- Business analysis
- SEO evaluation
- UX assessment
- Conversion optimization

### 3. **Automator Agent** 🤖
- Task automation
- Business process workflows
- Intelligent suggestions

### 4. **Session Management** 📁
- Create/delete sessions
- Rename conversations
- View message history
- Session summaries

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'xxx'`
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

**Error**: Port 8000 already in use
```bash
# Use different port
uvicorn main:app --port 8001
# Update frontend .env.local accordingly
```

### Frontend Won't Load

**Error**: `Cannot find module '@/components/Sidebar'`
- ✅ Already fixed! Re-check `app/page.tsx` imports

**Error**: API calls failing
- Ensure backend is running on http://localhost:8000
- Check `.env.local` has correct NEXT_PUBLIC_API_URL

### Database Issues

**Error**: SQLAlchemy connection error
- Delete `backend/agentsuite.db`
- Restart backend server

---

## 📝 Development Workflow

1. **Make code changes** in `frontend/` or `backend/`
2. **Frontend** auto-reloads via Turbopack
3. **Backend** auto-reloads with `--reload` flag
4. **Test** via browser (localhost:3000) or API client
5. **Commit** when satisfied

---

## 🎯 Next Steps

1. ✅ Project is ready to develop
2. Consider adding:
   - Docker compose for easy deployment
   - GitHub Actions CI/CD
   - Comprehensive error handling
   - Rate limiting & caching
   - WebSocket support for real-time updates
   - Database migrations (Alembic)

---

## 📞 Support

For issues:
1. Check this guide's troubleshooting section
2. Review logs in terminal outputs
3. Verify `.env` files are correctly configured
4. Ensure all dependencies are installed

---

**Status**: ✅ **PRODUCTION READY FOR DEVELOPMENT**

All systems operational. Happy coding! 🚀
