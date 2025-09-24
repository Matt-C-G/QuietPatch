#!/usr/bin/env bash
# Generate all icon formats from SVG source

set -e

SVG_SOURCE="assets/quietpatch-icon.svg"
ICONS_DIR="assets/icons"
OUTPUT_DIR="assets"

echo "Generating icons from $SVG_SOURCE..."

# Create icons directory
mkdir -p "$ICONS_DIR"

# Check if ImageMagick is available
if ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick not found. Please install it first:"
    echo "  macOS: brew install imagemagick"
    echo "  Ubuntu: sudo apt install imagemagick"
    echo "  Windows: choco install imagemagick"
    exit 1
fi

# Generate PNG icons in various sizes
echo "Generating PNG icons..."
for size in 1024 512 256 128 64 32 16; do
    echo "  Creating ${size}x${size} icon..."
    convert "$SVG_SOURCE" -resize "${size}x${size}" "$ICONS_DIR/icon-${size}.png"
done

# Generate Windows ICO
echo "Generating Windows ICO..."
convert "$ICONS_DIR/icon-256.png" "$ICONS_DIR/icon-128.png" "$ICONS_DIR/icon-64.png" "$ICONS_DIR/icon-32.png" "$ICONS_DIR/icon-16.png" "$OUTPUT_DIR/quietpatch.ico"

# Generate macOS ICNS
echo "Generating macOS ICNS..."
ICONSET_DIR="$OUTPUT_DIR/QuietPatch.iconset"
mkdir -p "$ICONSET_DIR"

# Create @2x versions
for size in 16 32 64 128 256 512; do
    cp "$ICONS_DIR/icon-$((size*2)).png" "$ICONSET_DIR/icon_${size}x${size}@2x.png"
done

# Create regular versions
for size in 16 32 128 256 512; do
    cp "$ICONS_DIR/icon-${size}.png" "$ICONSET_DIR/icon_${size}x${size}.png"
done

# Generate ICNS
iconutil -c icns "$ICONSET_DIR" -o "$OUTPUT_DIR/QuietPatch.icns"

# Clean up iconset directory
rm -rf "$ICONSET_DIR"

# Copy main PNG for Linux
cp "$ICONS_DIR/icon-256.png" "$OUTPUT_DIR/QuietPatch.png"

# Generate DMG background
echo "Generating DMG background..."
convert "$OUTPUT_DIR/dmg-bg.svg" -resize "800x500" "$OUTPUT_DIR/dmg-bg.png"

echo "✓ All icons generated successfully!"
echo ""
echo "Generated files:"
echo "  Windows ICO: $OUTPUT_DIR/quietpatch.ico"
echo "  macOS ICNS:  $OUTPUT_DIR/QuietPatch.icns"
echo "  Linux PNG:   $OUTPUT_DIR/QuietPatch.png"
echo "  DMG BG:      $OUTPUT_DIR/dmg-bg.png"
echo "  PNG sizes:   $ICONS_DIR/icon-*.png"
