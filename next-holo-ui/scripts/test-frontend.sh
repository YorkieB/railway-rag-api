#!/bin/bash
# Frontend Testing Script for Jarvis UI
# Tests all components and API connectivity

set -e

echo "=========================================="
echo "Frontend Testing Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}

echo "API Base URL: $API_BASE_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Check if API is running
echo "Checking API connectivity..."
if curl -s -f "$API_BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API is not running at $API_BASE_URL${NC}"
    echo "Please start the API first: cd rag-api && uvicorn app:app --reload"
    exit 1
fi

# Check if frontend is running
echo "Checking frontend connectivity..."
if curl -s -f "$FRONTEND_URL" > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend is not running at $FRONTEND_URL${NC}"
    echo "Please start the frontend first: cd next-holo-ui && npm run dev"
fi

echo ""
echo "=========================================="
echo "Testing API Endpoints"
echo "=========================================="

# Test endpoints
ENDPOINTS=(
    "/"
    "/health"
    "/metrics"
    "/memory?user_id=test"
    "/live-sessions?user_id=test"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "Testing $endpoint... "
    if curl -s -f "$API_BASE_URL$endpoint" > /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
done

echo ""
echo "=========================================="
echo "Component Checklist"
echo "=========================================="
echo "Please manually verify the following components:"
echo ""
echo "Core Components:"
echo "  [ ] BudgetStatus component renders"
echo "  [ ] MemoryPanel component renders"
echo "  [ ] BrowserPanel component renders"
echo "  [ ] UncertaintyBanner component renders"
echo ""
echo "Feature Components:"
echo "  [ ] ImageGenerator component renders"
echo "  [ ] SpotifyPlayer component renders"
echo "  [ ] MusicCreator component renders"
echo "  [ ] SocialMediaPoster component renders"
echo "  [ ] WordProcessor component renders"
echo ""
echo "UI Components:"
echo "  [ ] ThemeToggle works"
echo "  [ ] Dark mode switches correctly"
echo "  [ ] Buttons are clickable"
echo "  [ ] Cards display correctly"
echo ""
echo "API Integration:"
echo "  [ ] Components can fetch data from API"
echo "  [ ] Error states display correctly"
echo "  [ ] Loading states display correctly"
echo ""
echo "=========================================="
echo "Testing Complete"
echo "=========================================="

