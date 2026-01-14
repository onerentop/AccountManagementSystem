#!/bin/bash
# Account Management System - Docker Build & Deploy Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Account Management System - Deploy${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        # Generate random secret key
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
        sed -i "s/your-secure-secret-key-change-in-production/$SECRET_KEY/" .env
        echo -e "${GREEN}Generated secure SECRET_KEY${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Create data directory
mkdir -p data

# Parse command line arguments
ACTION=${1:-"up"}

case $ACTION in
    "build")
        echo -e "${YELLOW}Building Docker images...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}Build completed!${NC}"
        ;;
    "up")
        echo -e "${YELLOW}Starting services...${NC}"
        docker-compose up -d --build
        echo -e "${GREEN}Services started!${NC}"
        echo -e "${GREEN}Access the application at: http://localhost:${PORT:-8090}${NC}"
        ;;
    "down")
        echo -e "${YELLOW}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}Services stopped!${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}Restarting services...${NC}"
        docker-compose restart
        echo -e "${GREEN}Services restarted!${NC}"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "clean")
        echo -e "${YELLOW}Cleaning up...${NC}"
        docker-compose down -v --rmi local
        echo -e "${GREEN}Cleanup completed!${NC}"
        ;;
    *)
        echo "Usage: $0 {build|up|down|restart|logs|clean}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker images without cache"
        echo "  up      - Build and start services (default)"
        echo "  down    - Stop and remove containers"
        echo "  restart - Restart services"
        echo "  logs    - View logs"
        echo "  clean   - Remove containers, volumes, and images"
        exit 1
        ;;
esac
