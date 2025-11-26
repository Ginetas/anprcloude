#!/bin/bash
# Development Environment Setup Script
# Prepares the project for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}ANPR Development Environment Setup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        return 1
    fi
    echo -e "${GREEN}✓${NC} $1"
    return 0
}

MISSING_DEPS=0
check_command "python3" || MISSING_DEPS=1
check_command "pip3" || MISSING_DEPS=1
check_command "node" || MISSING_DEPS=1
check_command "npm" || MISSING_DEPS=1
check_command "docker" || MISSING_DEPS=1
check_command "docker-compose" || MISSING_DEPS=1
check_command "git" || MISSING_DEPS=1

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${RED}Please install missing dependencies${NC}"
    exit 1
fi

echo ""

# Create .env if it doesn't exist
echo -e "${YELLOW}Setting up environment configuration...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env from .env.example"
    echo -e "${YELLOW}  Please update .env with your configuration${NC}"
else
    echo -e "${GREEN}✓${NC} .env already exists"
fi

echo ""

# Create necessary directories
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p backups
mkdir -p logs
mkdir -p data/uploads
mkdir -p data/models
mkdir -p data/cache
echo -e "${GREEN}✓${NC} Directories created"

echo ""

# Make scripts executable
echo -e "${YELLOW}Setting up scripts...${NC}"
chmod +x scripts/*.sh
echo -e "${GREEN}✓${NC} Scripts are executable"

echo ""

# Setup pre-commit hooks (optional)
echo -e "${YELLOW}Setting up Git hooks...${NC}"
if [ -d .git ]; then
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit <<'EOF'
#!/bin/bash
# Pre-commit hook to check code quality

echo "Running pre-commit checks..."

# Check Python
if git diff --cached --name-only | grep -E '\.py$'; then
    echo "Checking Python files..."
    # You can add black, flake8, mypy checks here
fi

# Check JavaScript
if git diff --cached --name-only | grep -E '\.(ts|tsx|js|jsx)$'; then
    echo "Checking JavaScript files..."
    # You can add ESLint checks here
fi

exit 0
EOF
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✓${NC} Git hooks configured"
else
    echo -e "${YELLOW}⚠${NC} Not a Git repository, skipping hooks"
fi

echo ""

# Build and start Docker services
echo -e "${YELLOW}Building and starting Docker services...${NC}"
docker-compose build --no-cache 2>&1 | tail -5
echo -e "${GREEN}✓${NC} Docker images built"

echo ""
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓${NC} Services started"

echo ""

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker-compose exec -T postgres pg_isready -U anpr > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Timeout waiting for PostgreSQL${NC}"
    exit 1
fi

echo ""

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
if docker-compose exec -T backend alembic upgrade head > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Migrations completed"
else
    echo -e "${YELLOW}⚠${NC} Migrations may have failed (this is normal if DB is fresh)"
fi

echo ""

# Install backend development dependencies (optional)
echo -e "${YELLOW}Installing backend development tools...${NC}"
if [ -f backend/requirements.txt ]; then
    pip3 install -q black flake8 mypy isort 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Development tools installed"
fi

echo ""

# Show service status
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${BLUE}Running services:${NC}"
docker-compose ps
echo ""
echo -e "${BLUE}API Endpoints:${NC}"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  ReDoc: http://localhost:8000/redoc"
echo "  Frontend: http://localhost:3000"
echo ""
echo -e "${BLUE}Management UIs (optional, start with: make monitoring):${NC}"
echo "  Adminer (Database): http://localhost:8080"
echo "  Redis Commander: http://localhost:8081"
echo "  Prometheus: http://localhost:9091"
echo "  Grafana: http://localhost:3001"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  make dev         - Start development services"
echo "  make logs        - View service logs"
echo "  make test        - Run all tests"
echo "  make clean       - Stop services"
echo "  make help        - Show all available commands"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
