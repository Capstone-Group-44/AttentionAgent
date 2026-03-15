#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# build_macos.sh — Build Screen Gaze as a macOS .app and optional .dmg
#
# Usage:
#   bash build_macos.sh          # Build .app only
#   bash build_macos.sh --dmg    # Build .app + create DMG installer
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="Screen Gaze"
DMG_NAME="ScreenGaze"
BUILD_DMG=false

for arg in "$@"; do
    case "$arg" in
        --dmg) BUILD_DMG=true ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Building ${APP_NAME} for macOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Ensure we are in the right venv ──────────────────────────────
VENV_DIR="../.venv311"
if [ -d "$VENV_DIR" ]; then
    echo "→ Activating existing venv at $VENV_DIR"
    source "$VENV_DIR/bin/activate"
else
    echo "→ No .venv311 found — using current Python: $(python3 --version)"
fi

# ── 2. Install / upgrade PyInstaller ────────────────────────────────
echo "→ Ensuring PyInstaller is installed…"
pip install --upgrade pyinstaller 2>&1 | tail -1

# ── 3. Clean previous builds ────────────────────────────────────────
echo "→ Cleaning previous build artifacts…"
hdiutil detach "/Volumes/${APP_NAME}" 2>/dev/null || true
rm -rf build/ dist/

# ── 4. Run PyInstaller ──────────────────────────────────────────────
echo "→ Running PyInstaller…"
pyinstaller ScreenGaze.spec --noconfirm

# ── 5. Verify output ────────────────────────────────────────────────
APP_PATH="dist/${APP_NAME}.app"
if [ -d "$APP_PATH" ]; then
    echo ""
    echo "✅ Build succeeded!"
    echo "   App: $APP_PATH"
    echo "   Size: $(du -sh "$APP_PATH" | cut -f1)"
else
    echo "❌ Build failed — .app not found at $APP_PATH"
    exit 1
fi

# ── 6. Create DMG (optional) ────────────────────────────────────────
if [ "$BUILD_DMG" = true ]; then
    DMG_PATH="dist/${DMG_NAME}.dmg"
    DMG_TEMP="dist/${DMG_NAME}_temp.dmg"
    DMG_VOLUME="/Volumes/${APP_NAME}"

    echo ""
    echo "→ Creating DMG installer…"

    # Remove old DMG
    rm -f "$DMG_PATH" "$DMG_TEMP"

    # Calculate size (add 50MB headroom)
    APP_SIZE=$(du -sm "$APP_PATH" | cut -f1)
    DMG_SIZE=$((APP_SIZE + 50))

    # Create writable DMG
    hdiutil create -size "${DMG_SIZE}m" -fs HFS+ -volname "${APP_NAME}" "$DMG_TEMP"

    # Mount it
    hdiutil attach "$DMG_TEMP" -mountpoint "$DMG_VOLUME"

    # Copy app
    cp -R "$APP_PATH" "$DMG_VOLUME/"

    # Create Applications symlink for drag-install
    ln -s /Applications "$DMG_VOLUME/Applications"

    # Unmount
    hdiutil detach "$DMG_VOLUME"

    # Convert to compressed read-only DMG
    hdiutil convert "$DMG_TEMP" -format UDZO -o "$DMG_PATH"
    rm -f "$DMG_TEMP"

    echo ""
    echo "✅ DMG created!"
    echo "   DMG: $DMG_PATH"
    echo "   Size: $(du -sh "$DMG_PATH" | cut -f1)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done! To test, run:  open \"dist/${APP_NAME}.app\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
