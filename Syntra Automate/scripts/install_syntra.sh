#!/usr/bin/env bash
set -euo pipefail

# install_syntra.sh
# Idempotent installer for Syntra (Ubuntu 20.04/22.04/24.04)
# Run with sudo
if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo ./install_syntra.sh"
  exit 1
fi

# variables
APP_USER="syntra"
APP_DIR="/opt/syntra"
REPO_DIR="$APP_DIR/repo"
BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/frontend"
ENV_FILE="/etc/syntra.env"
PG_USER="syntra"
PG_DB="syntra_db"
PG_PASS="syntradb"
SYNTRA_FERNET_KEY=$(python3 - <<'PY'
from cryptography.fernet import Fernet
import base64
print(base64.urlsafe_b64encode(Fernet.generate_key()).decode())
PY
)

SYNTRA_SECRET=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c15)
MASTER_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c15)

echo "Creating system user $APP_USER (if not exists)..."
if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$APP_USER"
fi

echo "Creating dirs..."
mkdir -p "$APP_DIR"
chown $APP_USER:$APP_USER "$APP_DIR"

# Note: expects repo is already placed at $REPO_DIR; if not, we copy current directory
if [ ! -d "$REPO_DIR" ]; then
  echo "Copying repo to $REPO_DIR..."
  cp -r . "$REPO_DIR"
  chown -R $APP_USER:$APP_USER "$REPO_DIR"
fi

echo "Installing system packages..."
apt update
apt install -y python3 python3-venv python3-pip build-essential nginx ufw git nodejs npm postgresql

# PostgreSQL user and DB
echo "Configuring PostgreSQL..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$PG_DB';" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE $PG_DB;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$PG_USER';" | grep -q 1 || sudo -u postgres psql -c "CREATE USER $PG_USER WITH PASSWORD '$PG_PASS';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $PG_DB TO $PG_USER;"

# Backend venv
echo "Setting up Python virtualenv..."
python3 -m venv $APP_DIR/venv
$APP_DIR/venv/bin/pip install --upgrade pip
$APP_DIR/venv/bin/pip install -r $BACKEND_DIR/requirements.txt

# Environment file
cat > $ENV_FILE <<EOF
DATABASE_URL=postgresql+psycopg2://$PG_USER:$PG_PASS@localhost/$PG_DB
SYNTRA_SECRET=$SYNTRA_SECRET
SYNTRA_FERNET_KEY=$SYNTRA_FERNET_KEY
FRONTEND_ORIGIN=http://localhost:5173
MAX_CONCURRENT_SSH=6
EOF
chmod 640 $ENV_FILE
chown $APP_USER:$APP_USER $ENV_FILE

# Create master admin user in DB (if not exists)
echo "Creating master user in database..."
export PGPASSWORD=$PG_PASS
# We'll use a small Python snippet to create user if not exists
$APP_DIR/venv/bin/python3 - <<PY
import os
os.environ.update({'DATABASE_URL':'postgresql+psycopg2://$PG_USER:$PG_PASS@localhost/$PG_DB','SYNTRA_FERNET_KEY':'$SYNTRA_FERNET_KEY','SYNTRA_SECRET':'$SYNTRA_SECRET'})
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
from app import models
models.Base.metadata.create_all(bind=engine)
s = Session()
u = s.query(models.User).filter(models.User.username == 'syntra').first()
if not u:
    from app.auth import get_password_hash
    u = models.User(username='syntra', hashed_password=get_password_hash('$MASTER_PASSWORD'), role='admin')
    s.add(u); s.commit()
s.close()
print("MASTER_CREATED")
PY

# Expose credentials
CRED_FILE="/root/syntra_master_credentials.txt"
cat > $CRED_FILE <<EOF
username: syntra
password: $MASTER_PASSWORD
EOF
chmod 600 $CRED_FILE
echo "Master credentials written to $CRED_FILE"

# Create systemd service for backend
cat > /etc/systemd/system/syntra-backend.service <<SYS
[Unit]
Description=Syntra backend
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
EnvironmentFile=$ENV_FILE
WorkingDirectory=$BACKEND_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
SYS

systemctl daemon-reload
systemctl enable --now syntra-backend.service

# Frontend build (optional)
echo "Building frontend..."
cd $FRONTEND_DIR
npm install
npm run build
# Copy build artifacts to /var/www/syntra (served by nginx)
mkdir -p /var/www/syntra
cp -r dist/* /var/www/syntra/
chown -R www-data:www-data /var/www/syntra

# Nginx site
cat > /etc/nginx/sites-available/syntra <<NG
server {
    listen 80;
    server_name _;

    root /var/www/syntra;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
NG
ln -sf /etc/nginx/sites-available/syntra /etc/nginx/sites-enabled/syntra
nginx -t && systemctl reload nginx

# UFW
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw --force enable

echo "Installation done. Master credentials: $CRED_FILE"
echo "Frontend served at /var/www/syntra, backend on port 8000 (systemd syntra-backend)."
