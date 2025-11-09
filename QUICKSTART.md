# Quick Start Guide

## Installation (One-time Setup)

```bash
# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Enhance a Single Portrait

```bash
python enhance_portrait.py my_photo.jpg
```

This creates `my_photo_enhanced.jpg` in the same directory.

### 2. Batch Process Multiple Photos

```bash
# Process all .jpg files in a folder
python enhance_portrait.py -d /path/to/photos/

# Or process current directory
python enhance_portrait.py -d .
```

### 3. Custom Output Path

```bash
python enhance_portrait.py input.jpg -o output.jpg
```

## What the Script Does

The script automatically:
1. Removes top 10% (ceiling lights)
2. Fixes yellow/warm color tones
3. Enhances contrast and details
4. Sharpens eyes and hair
5. Smooths skin texture
6. Blurs background (depth of field)
7. Makes eyes brighter and more vibrant
8. Saves as high-quality JPEG

## Tips

- **Best results:** Use with portrait photos that have visible faces
- **Processing time:** 2-10 seconds per image depending on size
- **File naming:** Output files get `_enhanced` added to filename
- **Batch mode:** Already-enhanced files are automatically skipped

## Troubleshooting

### "No face detected" warning

The script will still process the image but skip face-specific enhancements. This happens when:
- No clear face is visible in the photo
- Face is too small or at extreme angle
- Very poor lighting

### Import errors

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

## Full Documentation

See [README.md](README.md) for complete documentation and technical details.
