#!/bin/bash
# ── Weblance Deployment Script for AWS EC2 Ubuntu ────────────────────
# Run this ON the EC2 server after SSH-ing in

set -e  # exit on any error

echo "=== Weblance Deployment ==="

# 1. Update system
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib libpq-dev python3-dev

# 2. Setup PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE weblance_db;" 2>/dev/null || echo "DB already exists"
sudo -u postgres psql -c "CREATE USER weblance_user WITH PASSWORD 'weblance123';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE weblance_db TO weblance_user;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER DATABASE weblance_db OWNER TO weblance_user;" 2>/dev/null || true

# 3. Clone / pull project
cd /home/ubuntu
if [ -d "weblance" ]; then
    echo "Pulling latest code..."
    cd weblance && git pull
else
    echo "Cloning project..."
    git clone https://github.com/YOUR_USERNAME/weblance.git weblance
    cd weblance
fi

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 6. Copy production .env
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo "⚠️  Edit .env with your actual values: nano .env"
fi

# 7. Run migrations & collect static
python manage.py migrate
python manage.py collectstatic --noinput

# 8. Create superuser (only first time)
echo "from django.contrib.auth.models import User; User.objects.filter(username='balakrishna').exists() or User.objects.create_superuser('balakrishna','infoweblance01@gmail.com','admin123')" | python manage.py shell

# 9. Setup Gunicorn systemd service
sudo tee /etc/systemd/system/weblance.service > /dev/null <<EOF
[Unit]
Description=Weblance Django App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/weblance
Environment="PATH=/home/ubuntu/weblance/venv/bin"
EnvironmentFile=/home/ubuntu/weblance/.env
ExecStart=/home/ubuntu/weblance/venv/bin/gunicorn weblance_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable weblance
sudo systemctl restart weblance

# 10. Setup Nginx
sudo tee /etc/nginx/sites-available/weblance > /dev/null <<EOF
server {
    listen 80;
    server_name 3.27.135.239 weblance.in www.weblance.in;

    location /static/ {
        alias /home/ubuntu/weblance/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/weblance/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/weblance /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo ""
echo "=== Deployment Complete ==="
echo "Site: http://3.27.135.239"
echo "Admin: http://3.27.135.239/panel/"
echo "Login: balakrishna / admin123"
