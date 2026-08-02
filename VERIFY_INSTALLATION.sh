#!/bin/bash
# Cortex Installation Verification Script

echo "==============================================="
echo "CORTEX INSTALLATION VERIFICATION"
echo "==============================================="
echo ""

PROJECT_DIR="/Users/rajalakshmisriram/cortex"

# Check if directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ ERROR: Project directory not found at $PROJECT_DIR"
    exit 1
fi

echo "✓ Project directory found: $PROJECT_DIR"
echo ""

# Count files
TOTAL_FILES=$(find "$PROJECT_DIR" -type f ! -path "*/.*" ! -path "*/build/*" ! -path "*/dist/*" ! -path "*/venv*" | wc -l)
echo "✓ Total files found: $TOTAL_FILES"
echo ""

# Check Python files
echo "PYTHON FILES:"
PY_COUNT=$(find "$PROJECT_DIR" -name "*.py" ! -path "*/build/*" ! -path "*/venv*" | wc -l)
echo "  Count: $PY_COUNT"
find "$PROJECT_DIR" -name "*.py" ! -path "*/build/*" ! -path "*/venv*" | sort | sed 's/^/    /'
echo ""

# Check Documentation
echo "DOCUMENTATION FILES:"
MD_COUNT=$(find "$PROJECT_DIR" -name "*.md" | wc -l)
TXT_COUNT=$(find "$PROJECT_DIR" -name "*.txt" | wc -l)
echo "  Markdown (.md): $MD_COUNT"
echo "  Text (.txt): $TXT_COUNT"
find "$PROJECT_DIR" -name "*.md" -o -name "*.txt" | sort | sed 's/^/    /'
echo ""

# Check important directories
echo "KEY DIRECTORIES:"
for dir in "app" "config" "skills" "macos-app"; do
    if [ -d "$PROJECT_DIR/$dir" ]; then
        count=$(find "$PROJECT_DIR/$dir" -type f | wc -l)
        echo "  ✓ $dir/ ($count files)"
    else
        echo "  ❌ $dir/ (NOT FOUND)"
    fi
done
echo ""

# Check executable scripts
echo "EXECUTABLE SCRIPTS:"
if [ -x "$PROJECT_DIR/build_macos_app.sh" ]; then
    echo "  ✓ build_macos_app.sh (executable)"
else
    echo "  ⚠ build_macos_app.sh (not executable, run: chmod +x)"
fi
echo ""

# Check critical files
echo "CRITICAL FILES:"
CRITICAL_FILES=(
    "cortex_gui.py"
    "setup.py"
    "requirements.txt"
    "build_macos_app.sh"
    "README.md"
    "BUILD_MACOS_APP.md"
)

ALL_FOUND=true
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        SIZE=$(ls -lh "$PROJECT_DIR/$file" | awk '{print $5}')
        echo "  ✓ $file ($SIZE)"
    else
        echo "  ❌ $file (MISSING)"
        ALL_FOUND=false
    fi
done
echo ""

# Summary
if [ "$ALL_FOUND" = true ]; then
    echo "==============================================="
    echo "✅ VERIFICATION SUCCESSFUL!"
    echo "==============================================="
    echo ""
    echo "All files are present and ready."
    echo ""
    echo "Next steps:"
    echo "1. cd /Users/rajalakshmisriram/cortex"
    echo "2. chmod +x build_macos_app.sh"
    echo "3. ./build_macos_app.sh"
    echo "4. open dist/Cortex.app"
    echo ""
else
    echo "==============================================="
    echo "❌ VERIFICATION FAILED!"
    echo "==============================================="
    echo "Some files are missing. Please check the output above."
    exit 1
fi
