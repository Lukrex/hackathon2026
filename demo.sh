#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🤝 Community Help System - Django Full Stack Demo         ║"
echo "║  HalovaMake Hackathon 2026                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_menu() {
    echo "Choose an option:"
    echo ""
    echo "  1️⃣  Install dependencies"
    echo "  2️⃣  Initialize database & create demo data"
    echo "  3️⃣  Create superuser (admin account)"
    echo "  4️⃣  Run development server"
    echo "  5️⃣  Run tests"
    echo "  6️⃣  Full setup (1+2+3+4)"
    echo "  7️⃣  Reset database (delete everything)"
    echo "  8️⃣  View API documentation"
    echo "  9️⃣  Exit"
    echo ""
}

install_deps() {
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed!${NC}"
}

init_db() {
    echo -e "${BLUE}🗄️  Initializing database...${NC}"
    python manage.py migrate
    python manage.py create_demo_data
    echo -e "${GREEN}✅ Database ready with demo data!${NC}"
}

create_admin() {
    echo -e "${BLUE}👤 Creating superuser account...${NC}"
    python manage.py createsuperuser
    echo -e "${GREEN}✅ Admin account created!${NC}"
}

run_server() {
    echo -e "${BLUE}🚀 Starting Django development server...${NC}"
    echo ""
    echo -e "${GREEN}✅ Server running at:${NC}"
    echo "   📊 Admin Dashboard: http://localhost:8000/admin/"
    echo "   📝 Submit Request: http://localhost:8000/submit/"
    echo "   🧠 API Root: http://localhost:8000/api/"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    python manage.py runserver
}

run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    python manage.py test
}

reset_db() {
    echo -e "${YELLOW}⚠️  WARNING: This will delete all data!${NC}"
    read -p "Are you sure? Type 'yes' to confirm: " confirm
    if [ "$confirm" = "yes" ]; then
        rm -f db.sqlite3
        echo -e "${BLUE}Initializing new database...${NC}"
        python manage.py migrate
        python manage.py create_demo_data
        echo -e "${GREEN}✅ Database reset!${NC}"
    else
        echo "Cancelled."
    fi
}

view_api_docs() {
    echo -e "${BLUE}📚 API Documentation${NC}"
    echo ""
    cat API_TESTING.md | less
}

full_setup() {
    install_deps
    echo ""
    init_db
    echo ""
    create_admin
    echo ""
    echo -e "${GREEN}✅ Full setup complete!${NC}"
    echo ""
    echo "Starting server in 3 seconds..."
    sleep 3
    run_server
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-9): " choice

    case $choice in
        1)
            install_deps
            ;;
        2)
            init_db
            ;;
        3)
            create_admin
            ;;
        4)
            run_server
            ;;
        5)
            run_tests
            ;;
        6)
            full_setup
            ;;
        7)
            reset_db
            ;;
        8)
            view_api_docs
            ;;
        9)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Invalid option. Please try again.${NC}"
            ;;
    esac

    read -p "Press Enter to continue..."
done
