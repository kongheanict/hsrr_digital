# Git Ignore Guide for Your Project

## Files Already Ignored

### Frontend (`frontend/.gitignore`)
- `node_modules/` - npm packages
- `dist/` - production build
- `.env`, `.env.local`, `.env.production` - environment variables
- `auto-imports.d.ts`, `components.d.ts` - auto-generated types
- IDE files (`.vscode/`, `.idea/`)

### Backend (`backend/.gitignore`)
- `venv/`, `env/` - Python virtual environment
- `*.pyc`, `__pycache__/` - Python compiled files
- `db.sqlite3` - SQLite database
- `/media`, `/staticfiles` - uploaded/static files
- `.env` - environment variables
- `debug.log` - debug logs

## Important: What to Keep in Git

### Frontend
✅ `package.json`, `package-lock.json` - dependency definitions
✅ `src/` - all source code
✅ `public/` - static assets
✅ `vite.config.ts`, `tsconfig.json` - configuration files

### Backend
✅ `requirements.txt` - Python dependencies
✅ `manage.py` - Django management script
✅ `apps/`, `server/` - application code
✅ `templates/` - Django templates
✅ `.env.example` - example environment variables (without secrets)

## Deployment Checklist

When deploying to a hosted server:

1. **Clone the repository** on the server
2. **Create `.env` files** with production values (not in git!)
3. **Frontend**: Run `npm install` then `npm run build`
4. **Backend**: Create venv, `pip install -r requirements.txt`
5. **Backend**: Run `python manage.py collectstatic`
6. **Backend**: Run migrations: `python manage.py migrate`

## Security Notes

🔒 **Never commit:**
- `.env` files with real credentials
- `db.sqlite3` (use PostgreSQL/MySQL in production)
- `node_modules/` or `venv/`
- API keys, passwords, secret keys
