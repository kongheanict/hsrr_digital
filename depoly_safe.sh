#!/bin/bash
# deploy_prod.sh - optimized safe deployment for Django + Vue

set -euo pipefail

# ===============================
# CONFIGURATION
# ===============================
PROJECT_DIR="/var/www/myschool_digital_django"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
GUNICORN_SERVICE="myschool_django"
LOG_FILE="$PROJECT_DIR/deploy.log"

# Backup directory (timestamped)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$PROJECT_DIR/backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# ===============================
# FUNCTIONS
# ===============================
echo_info()  { echo -e "\033[1;34m[INFO]\033[0m $1"; }
echo_warn()  { echo -e "\033[1;33m[WARN]\033[0m $1"; }
echo_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }

backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo_info "Backed up $file"
    fi
}

backup_dir() {
    local dir=$1
    if [ -d "$dir" ]; then
        rsync -a "$dir/" "$BACKUP_DIR/$(basename $dir)/"
        echo_info "Backed up $dir"
    fi
}

rollback() {
    echo_error "Deployment failed. Rolling back..."
    cp "$BACKUP_DIR/.env" "$BACKEND_DIR/.env" 2>/dev/null || echo_warn ".env backup not found"
    rsync -a "$BACKUP_DIR/static/" "$BACKEND_DIR/static/" 2>/dev/null || echo_warn "static backup not found"
    rsync -a "$BACKUP_DIR/media/" "$BACKEND_DIR/media/" 2>/dev/null || echo_warn "media backup not found"

    if [[ -f "$BACKUP_DIR/${DB_NAME}_$TIMESTAMP.dump" ]]; then
        echo_info "Restoring database..."
        export PGPASSWORD=$DB_PASSWORD
        pg_restore -U $DB_USER -d $DB_NAME -c "$BACKUP_DIR/${DB_NAME}_$TIMESTAMP.dump"
        unset PGPASSWORD
    fi
    echo_info "Rollback completed."
    exit 1
}

trap 'rollback' ERR

# ===============================
# DEPLOY STEPS
# ===============================
echo_info "1. Backing up .env, database, and static/media files"
backup_file "$BACKEND_DIR/.env"
backup_dir "$BACKEND_DIR/static"
backup_dir "$BACKEND_DIR/media"

# Parse DATABASE_URL from .env if exists
DB_URL=$(grep DATABASE_URL "$BACKEND_DIR/.env" | cut -d '=' -f2 || echo "")
if [[ -n "$DB_URL" ]]; then
    # Example: postgres://user:pass@localhost:5432/dbname
    DB_USER=$(echo $DB_URL | sed -E 's|postgres://([^:]+):.*|\1|')
    DB_PASSWORD=$(echo $DB_URL | sed -E 's|postgres://[^:]+:([^@]+)@.*|\1|')
    DB_HOST=$(echo $DB_URL | sed -E 's|postgres://[^:]+:[^@]+@([^:]+):.*|\1|')
    DB_PORT=$(echo $DB_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
    DB_NAME=$(echo $DB_URL | sed -E 's|.*/([^/]+)$|\1|')
fi

# Optional: backup PostgreSQL database
if [[ -n "$DB_NAME" ]]; then
    echo_info "Backing up PostgreSQL database"
    export PGPASSWORD=$DB_PASSWORD
    pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT -F c $DB_NAME > "$BACKUP_DIR/${DB_NAME}_$TIMESTAMP.dump"
    unset PGPASSWORD
    echo_info "Database backup saved to $BACKUP_DIR/${DB_NAME}_$TIMESTAMP.dump"
fi

echo_info "2. Pull latest code from Git"
cd $PROJECT_DIR
git fetch origin
git reset --hard origin/main

echo_info "3. Activate virtual environment"
source "$VENV_DIR/bin/activate"

echo_info "4. Install/update Python dependencies"
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

echo_info "5. Build Vue frontend"
cd $FRONTEND_DIR
npm ci
npm run build

echo_info "6. Collect static files"
cd $BACKEND_DIR
python manage.py collectstatic --noinput

echo_info "7. Apply database migrations"
python manage.py migrate --noinput

echo_info "8. Restart Gunicorn service"
sudo systemctl restart $GUNICORN_SERVICE

echo_info "9. Health check"
if curl -s -f http://localhost/ > /dev/null; then
    echo_info "Health check passed!"
else
    echo_error "Health check failed!"
    rollback
fi

echo_info "Deployment completed successfully!"
echo_info "Backups stored at $BACKUP_DIR"

# Save log
echo_info "Deployment finished at $(date)" >> $LOG_FILE
