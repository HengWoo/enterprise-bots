# Campfire AI Bot

AI-powered chatbot for Campfire using Claude Agent SDK. Provides intelligent responses based on conversation context, user preferences, and company knowledge base.

## Features

- **Conversation Search**: Search through message history to provide context-aware responses
- **User Context Management**: Remember user preferences, expertise, and conversation history
- **Mock Database**: Comprehensive test database for local development
- **Docker Support**: Containerized deployment for easy production setup
- **TDD Approach**: 100% test coverage with comprehensive test suite

## Project Structure

```
campfire-ai-bot/
├── src/
│   ├── app.py                 # Flask webhook server
│   └── tools/
│       └── campfire_tools.py  # Campfire tools for Agent SDK
├── tests/
│   ├── test_app.py            # Flask app tests
│   ├── test_tools.py          # Tools tests
│   └── fixtures/
│       ├── setup_test_db.py   # Mock database creation
│       └── test.db            # Generated test database
├── pyproject.toml             # uv project configuration
├── Dockerfile                 # Docker build configuration
├── docker-compose.yml         # Docker Compose setup
└── .env.example               # Environment template
```

## Quick Start

### Local Development

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**:
   ```bash
   cd /Users/heng/Development/campfire/ai-bot
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**:
   ```bash
   uv sync --all-extras
   ```

4. **Create test database**:
   ```bash
   uv run python tests/fixtures/setup_test_db.py
   ```

5. **Run tests**:
   ```bash
   uv run pytest tests/ -v
   ```

6. **Run development server**:
   ```bash
   uv run python src/app.py
   ```

### Docker Deployment

1. **Build image**:
   ```bash
   docker build -t campfire-ai-bot:latest .
   ```

2. **Run with Docker Compose** (for local testing):
   ```bash
   docker-compose up -d
   ```

3. **Check health**:
   ```bash
   curl http://localhost:5000/health
   ```

## Production Deployment (DigitalOcean)

### Prerequisites
- DigitalOcean droplet (Ubuntu 22.04)
- Campfire running at chat.smartice.ai
- Bot created in Campfire with bot_key

### Step 1: Prepare Server

SSH into your droplet:
```bash
ssh root@128.199.175.50
```

Install Docker:
```bash
apt update
apt install -y docker.io docker-compose
systemctl start docker
systemctl enable docker
```

### Step 2: Transfer Docker Image

On local machine, save image:
```bash
docker save campfire-ai-bot:latest | gzip > campfire-ai-bot.tar.gz
```

Transfer to server:
```bash
scp campfire-ai-bot.tar.gz root@128.199.175.50:/root/
```

On server, load image:
```bash
cd /root
docker load < campfire-ai-bot.tar.gz
rm campfire-ai-bot.tar.gz
```

### Step 3: Configure Environment

Create `/root/ai-service/.env`:
```bash
mkdir -p /root/ai-service
cat > /root/ai-service/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CAMPFIRE_URL=https://chat.smartice.ai
BOT_KEY=2-CsheovnLtzjM
CAMPFIRE_DB_PATH=/var/once/campfire/db/production.sqlite3
CONTEXT_DIR=/app/user_contexts
SYSTEM_PROMPT=You are a professional financial analyst AI assistant in Campfire. You provide clear, actionable insights based on conversation context and user preferences.
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
LOG_LEVEL=INFO
EOF
```

### Step 4: Create Docker Compose

Create `/root/ai-service/docker-compose.yml`:
```yaml
version: '3.8'

services:
  campfire-bot:
    image: campfire-ai-bot:latest
    container_name: campfire-bot
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      # Mount Campfire database (read-only)
      - /var/once/campfire/db:/data/campfire/db:ro
      # Persistent user contexts
      - ./user_contexts:/app/user_contexts
    restart: unless-stopped
```

### Step 5: Start Service

```bash
cd /root/ai-service
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f
```

### Step 6: Configure Campfire Webhook

1. Go to Campfire admin panel
2. Navigate to bot settings for "财务分析师"
3. Add webhook URL: `http://128.199.175.50:5000/webhook`
4. Save configuration

### Step 7: Test E2E

1. Go to any room where the bot is a member
2. Send message: `@财务分析师 Hello!`
3. Bot should respond within a few seconds

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `CAMPFIRE_URL` | Campfire base URL | `https://chat.smartice.ai` |
| `BOT_KEY` | Bot authentication key | `2-CsheovnLtzjM` |
| `CAMPFIRE_DB_PATH` | Path to Campfire database | `./tests/fixtures/test.db` |
| `CONTEXT_DIR` | User context storage directory | `./user_contexts` |
| `SYSTEM_PROMPT` | Bot personality/instructions | Financial analyst prompt |
| `FLASK_PORT` | Flask server port | `5000` |
| `FLASK_HOST` | Flask server host | `0.0.0.0` |
| `LOG_LEVEL` | Logging level | `INFO` |

## API Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00.123456"
}
```

### `POST /webhook`
Campfire webhook endpoint

**Request:**
```json
{
  "creator": {
    "id": 1,
    "name": "User Name",
    "email_address": "user@example.com"
  },
  "room": {
    "id": 2,
    "name": "Finance Team"
  },
  "content": "<p>@bot Your message here</p>"
}
```

**Response:**
```json
{
  "status": "success"
}
```

## Testing

Run all tests:
```bash
uv run pytest tests/ -v
```

Run specific test file:
```bash
uv run pytest tests/test_tools.py -v
```

Run with coverage:
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## Development

### Adding New Tools

1. Add method to `CampfireTools` class in `src/tools/campfire_tools.py`
2. Write tests first in `tests/test_tools.py`
3. Implement to make tests pass
4. Register tool with Agent SDK in `src/app.py`

### Database Schema

See `DESIGN.md` for complete database schema documentation.

Key tables:
- `users`: User accounts
- `rooms`: Chat rooms
- `messages`: Message records
- `action_text_rich_texts`: Message bodies (HTML)
- `memberships`: User-room relationships

## Troubleshooting

### Bot not responding
1. Check Docker logs: `docker-compose logs -f`
2. Verify webhook is configured in Campfire
3. Test health endpoint: `curl http://localhost:5000/health`
4. Check API key is valid

### Database errors
1. Verify database path is correct
2. Check database file permissions (read-only access needed)
3. Ensure SQLite WAL mode is enabled

### Import errors
1. Reinstall dependencies: `uv sync --all-extras`
2. Verify Python version: `python --version` (should be 3.10+)

## Architecture

See `DESIGN.md` for complete architectural documentation.

**Key Principles:**
- Read-only database access (Campfire DB is managed by ONCE)
- External storage for AI service (survives ONCE updates)
- Consolidated tools following Anthropic best practices
- Test-driven development

## License

Proprietary - SmartICE AI

## Support

For issues or questions, contact heng.woo@gmail.com
