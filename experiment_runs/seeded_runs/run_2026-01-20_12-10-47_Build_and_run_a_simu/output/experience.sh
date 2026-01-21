#!/bin/bash

###############################################################################
# Boids Simulation - Complete Experience Script
#
# A unified launcher for all the different ways to experience this simulation.
# Run this to see a menu of options.
#
# Usage: ./experience.sh [option]
#   or just: ./experience.sh  (shows menu)
###############################################################################

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print header
print_header() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}║           ${YELLOW}🐦 BOIDS FLOCKING SIMULATION 🐦${CYAN}              ║${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}║        Emergent behavior from simple rules                 ║${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Print menu
print_menu() {
    echo -e "${GREEN}Choose your experience:${NC}"
    echo ""
    echo -e "  ${YELLOW}1)${NC} Interactive Playground     - Open index.html (full UI)"
    echo -e "  ${YELLOW}2)${NC} Terminal Visualization     - ASCII art in terminal (no browser!)"
    echo -e "  ${YELLOW}3)${NC} Quick Demo                 - Headless simulation with metrics"
    echo -e "  ${YELLOW}4)${NC} Run All Tests             - Verify everything works (51 tests)"
    echo -e "  ${YELLOW}5)${NC} Performance Benchmark      - Validate optimization choices"
    echo -e "  ${YELLOW}6)${NC} Final Verification        - Complete production readiness check"
    echo -e "  ${YELLOW}7)${NC} Read Documentation        - Open START_HERE.md"
    echo -e "  ${YELLOW}8)${NC} Workshop (if available)   - Guided 8-lesson learning"
    echo ""
    echo -e "  ${YELLOW}q)${NC} Quit"
    echo ""
}

# Run interactive playground
run_playground() {
    echo -e "${GREEN}🚀 Launching interactive playground...${NC}"
    if command -v open &> /dev/null; then
        open index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open index.html
    else
        echo -e "${RED}Could not find a command to open files.${NC}"
        echo -e "Please open ${YELLOW}index.html${NC} manually in your browser."
    fi
}

# Run terminal visualization
run_terminal() {
    echo -e "${GREEN}🎨 Starting terminal visualization...${NC}"
    echo ""
    if [ -f "visualize-behavior.js" ]; then
        node visualize-behavior.js
    else
        echo -e "${RED}Error: visualize-behavior.js not found${NC}"
    fi
}

# Run quick demo
run_demo() {
    echo -e "${GREEN}⚡ Running quick demo...${NC}"
    echo ""
    if [ -f "quick-demo.js" ]; then
        node quick-demo.js
    else
        echo -e "${RED}Error: quick-demo.js not found${NC}"
    fi
}

# Run tests
run_tests() {
    echo -e "${GREEN}🧪 Running all tests...${NC}"
    echo ""

    echo -e "${CYAN}Vector Tests (27 tests):${NC}"
    node run-tests.js
    echo ""

    echo -e "${CYAN}Boid Tests (12 tests):${NC}"
    node run-boid-tests.js
    echo ""

    echo -e "${CYAN}Simulation Tests (12 tests):${NC}"
    node run-simulation-tests.js
    echo ""

    echo -e "${GREEN}✅ Total: 51 tests${NC}"
}

# Run performance benchmark
run_benchmark() {
    echo -e "${GREEN}📊 Running performance benchmark...${NC}"
    echo ""
    if [ -f "performance-benchmark.js" ]; then
        node performance-benchmark.js
    else
        echo -e "${RED}Error: performance-benchmark.js not found${NC}"
    fi
}

# Run final verification
run_verification() {
    echo -e "${GREEN}✅ Running final verification...${NC}"
    echo ""
    if [ -f "final-verification.js" ]; then
        node final-verification.js
    elif [ -f "verify-simulation-ready.js" ]; then
        node verify-simulation-ready.js
    else
        echo -e "${RED}Error: verification script not found${NC}"
    fi
}

# Read documentation
read_docs() {
    echo -e "${GREEN}📖 Opening documentation...${NC}"
    if command -v less &> /dev/null; then
        less START_HERE.md
    elif command -v more &> /dev/null; then
        more START_HERE.md
    else
        cat START_HERE.md
    fi
}

# Run workshop
run_workshop() {
    echo -e "${GREEN}🎓 Launching workshop...${NC}"
    if [ -f "workshop.html" ]; then
        if command -v open &> /dev/null; then
            open workshop.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open workshop.html
        else
            echo -e "${RED}Could not find a command to open files.${NC}"
            echo -e "Please open ${YELLOW}workshop.html${NC} manually in your browser."
        fi
    else
        echo -e "${YELLOW}Workshop not available yet.${NC}"
        echo -e "Try the interactive playground instead: ${CYAN}open index.html${NC}"
    fi
}

# Main menu loop
main_menu() {
    while true; do
        print_header
        print_menu

        read -p "Enter your choice: " choice
        echo ""

        case $choice in
            1) run_playground ;;
            2) run_terminal ;;
            3) run_demo ;;
            4) run_tests ;;
            5) run_benchmark ;;
            6) run_verification ;;
            7) read_docs ;;
            8) run_workshop ;;
            q|Q)
                echo -e "${GREEN}Thanks for exploring the boids simulation! 🐦${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice. Please try again.${NC}"
                ;;
        esac

        echo ""
        read -p "Press Enter to return to menu..."
    done
}

# Handle command line argument
if [ $# -eq 1 ]; then
    case $1 in
        playground|1) run_playground ;;
        terminal|2) run_terminal ;;
        demo|3) run_demo ;;
        tests|4) run_tests ;;
        benchmark|5) run_benchmark ;;
        verify|6) run_verification ;;
        docs|7) read_docs ;;
        workshop|8) run_workshop ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo -e "Usage: $0 [playground|terminal|demo|tests|benchmark|verify|docs|workshop]"
            exit 1
            ;;
    esac
else
    main_menu
fi
