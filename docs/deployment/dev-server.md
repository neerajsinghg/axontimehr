# Remote Linux VM DEV Server Deployment Guide

## Server Requirements
- **OS**: Ubuntu 22.04 LTS / 24.04 LTS
- **CPU**: 2+ Cores
- **RAM**: 4GB+ RAM
- **Disk**: 20GB+ SSD

## Deployment Setup

```bash
# 1. Install Docker & Docker Compose on Ubuntu
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git

# 2. Clone repository
cd /opt
sudo git clone https://github.com/axontimehr/axontimehr.git
cd axontimehr

# 3. Configure production environment
sudo cp .env.example .env
# Edit .env with secure passwords

# 4. Start production stack
sudo docker compose up -d

# 5. Verify service health
sudo docker compose ps
```
