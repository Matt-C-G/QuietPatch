#!/bin/bash
# macOS DMG creation script for QuietPatch v0.4.0

set -e

# Configuration
APP_NAME="QuietPatch"
VERSION="0.4.0"
DMG_NAME="${APP_NAME}-v${VERSION}"
APP_PATH="dist/macos/${APP_NAME}.app"
DMG_PATH="dist/macos/${DMG_NAME}.dmg"
BACKGROUND_IMAGE="assets/dmg-background.png"
ICON_SIZE=100
WINDOW_WIDTH=600
WINDOW_HEIGHT=400

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating macOS DMG for ${APP_NAME} v${VERSION}${NC}"

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo -e "${YELLOW}create-dmg not found. Installing via Homebrew...${NC}"
    if command -v brew &> /dev/null; then
        brew install create-dmg
    else
        echo -e "${RED}Error: Homebrew not found. Please install create-dmg manually.${NC}"
        echo "Visit: https://github.com/create-dmg/create-dmg"
        exit 1
    fi
fi

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}Error: App not found at $APP_PATH${NC}"
    echo "Please build the app first using PyInstaller"
    exit 1
fi

# Create dist/macos directory if it doesn't exist
mkdir -p dist/macos

# Create background image if it doesn't exist
if [ ! -f "$BACKGROUND_IMAGE" ]; then
    echo -e "${YELLOW}Creating default background image...${NC}"
    mkdir -p assets
    # Create a simple background image using ImageMagick if available
    if command -v convert &> /dev/null; then
        convert -size 600x400 xc:'#f0f0f0' -fill '#2c3e50' -pointsize 24 -gravity center -annotate +0+0 "QuietPatch\nPrivacy-first patch advisor" "$BACKGROUND_IMAGE"
    else
        echo -e "${YELLOW}ImageMagick not found. Using default background.${NC}"
        # Create a simple placeholder
        echo "DMG Background" > "$BACKGROUND_IMAGE"
    fi
fi

# Clean up any existing DMG
if [ -f "$DMG_PATH" ]; then
    echo -e "${YELLOW}Removing existing DMG...${NC}"
    rm "$DMG_PATH"
fi

# Create the DMG
echo -e "${GREEN}Creating DMG...${NC}"
create-dmg \
    --volname "${APP_NAME} v${VERSION}" \
    --volicon "assets/quietpatch.icns" \
    --background "$BACKGROUND_IMAGE" \
    --window-pos 200 120 \
    --window-size $WINDOW_WIDTH $WINDOW_HEIGHT \
    --icon-size $ICON_SIZE \
    --icon "${APP_NAME}.app" 100 200 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 400 200 \
    --no-internet-enable \
    "$DMG_PATH" \
    "$APP_PATH"

# Verify DMG was created
if [ -f "$DMG_PATH" ]; then
    echo -e "${GREEN}✓ DMG created successfully: $DMG_PATH${NC}"
    
    # Show DMG info
    echo -e "${GREEN}DMG Information:${NC}"
    hdiutil imageinfo "$DMG_PATH" | grep -E "(Checksum|Format|Size)"
    
    # Create checksum
    echo -e "${GREEN}Creating SHA256 checksum...${NC}"
    shasum -a 256 "$DMG_PATH" > "${DMG_PATH}.sha256"
    echo "Checksum saved to: ${DMG_PATH}.sha256"
    
else
    echo -e "${RED}Error: Failed to create DMG${NC}"
    exit 1
fi

echo -e "${GREEN}✓ macOS DMG packaging complete!${NC}"
