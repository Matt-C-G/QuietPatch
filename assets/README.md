# Assets Directory

This directory contains assets for the QuietPatch installer and packaging.

## Required Files

- `quietpatch.ico` - Windows icon file (256x256 ICO format)
- `quietpatch.icns` - macOS icon file (ICNS format)
- `quietpatch.png` - Linux icon file (256x256 PNG format)
- `dmg-background.png` - macOS DMG background image (600x400 PNG format)

## Creating Icons

You can create these icons from a single high-resolution PNG (512x512 or larger) using online converters or tools like:

- **ICO**: Use online converters or ImageMagick: `convert input.png -resize 256x256 output.ico`
- **ICNS**: Use `iconutil` on macOS or online converters
- **PNG**: Resize to 256x256: `convert input.png -resize 256x256 output.png`

## Placeholder

For now, the build scripts will create placeholder icons if these files don't exist.
