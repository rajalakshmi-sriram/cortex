#!/bin/bash
set -e

echo "=========================================="
echo "Cortex macOS App Builder"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ── 1. Find Python 3.11 ──────────────────────────────────────────────────────
echo "Checking requirements..."

PYTHON=""
for candidate in python3.11 python3.12 python3.10 python3; do
    if command -v "$candidate" &>/dev/null; then
        VER=$("$candidate" -c "import sys; print(sys.version_info[:2])")
        if [[ "$VER" == "(3, 11)" || "$VER" == "(3, 12)" || "$VER" == "(3, 10)" ]]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    echo "❌ ERROR: Python 3.10, 3.11 or 3.12 is required."
    echo ""
    echo "Install it with Homebrew:"
    echo "   brew install python@3.11"
    echo ""
    echo "Then re-run this script."
    exit 1
fi

echo "✓ Using Python: $PYTHON ($($PYTHON --version))"

# ── 2. Virtual environment ────────────────────────────────────────────────────
echo ""
echo "Creating virtual environment..."

rm -rf venv-build
"$PYTHON" -m venv venv-build
source venv-build/bin/activate
pip install --upgrade pip setuptools wheel -q
echo "✓ Virtual environment ready"

# ── 3. Install dependencies ───────────────────────────────────────────────────
echo ""
echo "Installing dependencies..."

pip install -q \
    "setuptools>=70" \
    "Flask==2.3.0" \
    "Flask-CORS==4.0.0" \
    "requests==2.31.0" \
    "python-dotenv==1.0.0" \
    "scikit-learn==1.3.2" \
    "numpy==1.24.4" \
    "pandas==2.0.3" \
    "beautifulsoup4==4.12.0" \
    "lxml==4.9.3" \
    "feedparser==6.0.10" \
    "PyYAML==6.0.1" \
    "PyQt6==6.6.0" \
    "py2app==0.28.7"

echo "✓ Dependencies installed"

# Verify pkg_resources is importable before proceeding
python -c "import pkg_resources" || {
    echo "❌ ERROR: pkg_resources still missing after installing setuptools."
    exit 1
}

# ── 4. Clean old builds ───────────────────────────────────────────────────────
echo ""
echo "Cleaning previous builds..."
rm -rf build dist
echo "✓ Clean done"

# ── 5. Build app bundle ───────────────────────────────────────────────────────
echo ""
echo "Building app bundle (this takes 2-3 minutes)..."

if ! "$PYTHON" setup.py py2app; then
    echo ""
    echo "❌ ERROR: py2app build failed. See output above."
    exit 1
fi

if [ ! -d "dist/Cortex.app" ]; then
    echo ""
    echo "❌ ERROR: Build did not produce dist/Cortex.app"
    exit 1
fi

echo "✓ App bundle created"

# ── 6. Create DMG ────────────────────────────────────────────────────────────
echo ""
echo "Creating DMG installer..."

APP_NAME="Cortex"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
TMP_DIR="/tmp/cortex-dmg-$$"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"
cp -r "dist/Cortex.app" "$TMP_DIR/"
ln -s /Applications "$TMP_DIR/Applications"

hdiutil create \
    -volname "$APP_NAME $VERSION" \
    -srcfolder "$TMP_DIR" \
    -ov -format UDZO \
    "dist/$DMG_NAME" 2>/dev/null

rm -rf "$TMP_DIR"
echo "✓ DMG created: dist/$DMG_NAME"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "✅ Build Complete!"
echo "=========================================="
echo ""
echo "  App:  dist/Cortex.app"
echo "  DMG:  dist/$DMG_NAME"
echo ""
echo "To run the app:"
echo "  open dist/Cortex.app"
echo ""
echo "To install from DMG:"
echo "  open dist/$DMG_NAME"
echo "  → Drag Cortex to Applications"
echo ""
