#!/bin/bash
# Linux AppImage creation script for QuietPatch v0.4.0

set -e

# Configuration
APP_NAME="QuietPatch"
VERSION="0.4.0"
APPIMAGE_NAME="${APP_NAME}-v${VERSION}-x86_64.AppImage"
APP_PATH="dist/linux/${APP_NAME}"
APPIMAGE_PATH="dist/linux/${APPIMAGE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating Linux AppImage for ${APP_NAME} v${VERSION}${NC}"

# Check if appimagetool is installed
if ! command -v appimagetool &> /dev/null; then
    echo -e "${YELLOW}appimagetool not found. Installing...${NC}"
    
    # Download appimagetool
    APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    APPIMAGETOOL_PATH="/tmp/appimagetool"
    
    echo "Downloading appimagetool..."
    wget -O "$APPIMAGETOOL_PATH" "$APPIMAGETOOL_URL"
    chmod +x "$APPIMAGETOOL_PATH"
    
    # Add to PATH for this session
    export PATH="/tmp:$PATH"
fi

# Check if app exists
if [ ! -f "$APP_PATH" ]; then
    echo -e "${RED}Error: App not found at $APP_PATH${NC}"
    echo "Please build the app first using PyInstaller"
    exit 1
fi

# Create dist/linux directory if it doesn't exist
mkdir -p dist/linux

# Create AppDir structure
APP_DIR="dist/linux/AppDir"
echo -e "${GREEN}Creating AppDir structure...${NC}"

# Clean up existing AppDir
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"

# Copy the binary
cp "$APP_PATH" "$APP_DIR/"

# Create desktop file
cat > "$APP_DIR/QuietPatch.desktop" << EOF
[Desktop Entry]
Type=Application
Name=QuietPatch
Comment=Privacy-first patch advisor
Exec=QuietPatch
Icon=QuietPatch
Categories=Utility;System;Security;
StartupNotify=true
Terminal=false
MimeType=application/x-quietpatch-report;
EOF

# Create AppRun script
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/QuietPatch" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# Create icon (if available)
if [ -f "assets/quietpatch.png" ]; then
    cp "assets/quietpatch.png" "$APP_DIR/QuietPatch.png"
else
    echo -e "${YELLOW}No icon found, creating placeholder...${NC}"
    # Create a simple placeholder icon using ImageMagick if available
    if command -v convert &> /dev/null; then
        convert -size 256x256 xc:'#2c3e50' -fill white -pointsize 48 -gravity center -annotate +0+0 "QP" "$APP_DIR/QuietPatch.png"
    else
        echo -e "${YELLOW}ImageMagick not found. Using default icon.${NC}"
        # Create a simple text file as placeholder
        echo "QuietPatch Icon" > "$APP_DIR/QuietPatch.png"
    fi
fi

# Create usr/bin directory and copy resources
mkdir -p "$APP_DIR/usr/bin"
cp "$APP_PATH" "$APP_DIR/usr/bin/"

# Copy catalog and policies if they exist
if [ -d "catalog" ]; then
    cp -r catalog "$APP_DIR/"
fi
if [ -d "policies" ]; then
    cp -r policies "$APP_DIR/"
fi
if [ -d "config" ]; then
    cp -r config "$APP_DIR/"
fi

# Create AppImage
echo -e "${GREEN}Creating AppImage...${NC}"
appimagetool "$APP_DIR" "$APPIMAGE_PATH"

# Verify AppImage was created
if [ -f "$APPIMAGE_PATH" ]; then
    echo -e "${GREEN}✓ AppImage created successfully: $APPIMAGE_PATH${NC}"
    
    # Make it executable
    chmod +x "$APPIMAGE_PATH"
    
    # Show AppImage info
    echo -e "${GREEN}AppImage Information:${NC}"
    file "$APPIMAGE_PATH"
    ls -lh "$APPIMAGE_PATH"
    
    # Create checksum
    echo -e "${GREEN}Creating SHA256 checksum...${NC}"
    shasum -a 256 "$APPIMAGE_PATH" > "${APPIMAGE_PATH}.sha256"
    echo "Checksum saved to: ${APPIMAGE_PATH}.sha256"
    
    # Test the AppImage (optional)
    echo -e "${GREEN}Testing AppImage...${NC}"
    if "$APPIMAGE_PATH" --help &> /dev/null; then
        echo -e "${GREEN}✓ AppImage test passed${NC}"
    else
        echo -e "${YELLOW}⚠ AppImage test failed (this might be normal for GUI apps)${NC}"
    fi
    
else
    echo -e "${RED}Error: Failed to create AppImage${NC}"
    exit 1
fi

# Clean up
rm -rf "$APP_DIR"

echo -e "${GREEN}✓ Linux AppImage packaging complete!${NC}"
