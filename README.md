# Image Enhancement Script

A professional-grade Python script for enhancing portrait photographs with automatic facial feature detection and multi-step enhancement pipeline.

## Features

This script applies the following enhancements to portrait photographs:

1. **Auto-crop** - Removes 10% from the top of the image (eliminates ceiling lights)
2. **White Balance** - Reduces warm/yellow tones using neutral white point assumption
3. **Contrast Enhancement** - Uses CLAHE to enhance facial features
4. **Local Sharpening** - Sharpens eyes and hair using MediaPipe facial landmark detection
5. **Skin Smoothing** - Applies subtle smoothing using bilateral filter while preserving detail
6. **Background Blur** - Darkens and blurs background to emphasize subject (depth of field simulation)
7. **Eye Enhancement** - Increases eye brightness and saturation subtly
8. **High-Quality Output** - Saves as JPEG with 95% quality, adding `_enhanced` suffix to filename

## Requirements

- **Operating System**: CachyOS (Arch-based Linux) or any Linux distribution
- **Python**: 3.8 or higher
- **Libraries**: All open-source and installable via pip

### Dependencies

```
opencv-python >= 4.8.0
numpy >= 1.24.0
mediapipe >= 0.10.0
Pillow >= 10.0.0
```

## Installation

### On CachyOS/Arch Linux

1. **Install Python and pip** (if not already installed):
   ```bash
   sudo pacman -S python python-pip
   ```

2. **Clone or download this repository**:
   ```bash
   git clone https://github.com/ampedup811-create/image_enhance.git
   cd image_enhance
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install packages individually:
   ```bash
   pip install opencv-python numpy mediapipe Pillow
   ```

### Alternative: Using pacman for some packages

Some dependencies may be available through pacman:
```bash
sudo pacman -S python-numpy python-pillow
pip install opencv-python mediapipe
```

## Usage

### Single Image Enhancement

Process a single portrait image:

```bash
python enhance_portrait.py portrait.jpg
```

This will create `portrait_enhanced.jpg` in the same directory.

#### Custom Output Path

Specify a custom output path:

```bash
python enhance_portrait.py portrait.jpg -o /path/to/output.jpg
```

### Batch Processing

Process all `.jpg` files in a directory:

```bash
python enhance_portrait.py -d /path/to/photos/
```

Process all `.jpg` files in the current directory:

```bash
python enhance_portrait.py -d .
```

**Note**: Files with `_enhanced` in the name are automatically skipped to avoid reprocessing.

### Getting Help

View all available options:

```bash
python enhance_portrait.py --help
```

## How It Works

### Facial Landmark Detection

The script uses **MediaPipe Face Mesh** to detect 478 facial landmarks, enabling:
- Precise eye region detection for sharpening and enhancement
- Face boundary detection for skin smoothing
- Subject segmentation for background blur

### Enhancement Pipeline

```
Input Image
    ↓
[1] Auto-crop top 10%
    ↓
[2] White balance adjustment (gray world algorithm)
    ↓
[3] Contrast enhancement (CLAHE on L channel)
    ↓
[4] Detect facial landmarks (MediaPipe)
    ↓
[5] Sharpen eyes and hair regions
    ↓
[6] Apply bilateral filter skin smoothing
    ↓
[7] Blur and darken background
    ↓
[8] Enhance eye brightness and saturation
    ↓
Save as high-quality JPEG (95% quality)
```

### Algorithms Used

- **White Balance**: Gray World Assumption
- **Contrast**: CLAHE (Contrast Limited Adaptive Histogram Equalization)
- **Sharpening**: Unsharp Masking
- **Skin Smoothing**: Bilateral Filter (edge-preserving)
- **Background Blur**: Gaussian Blur with subject mask
- **Eye Enhancement**: HSV color space manipulation

## Examples

### Basic Usage

```bash
# Enhance a single portrait
python enhance_portrait.py my_photo.jpg

# Output: my_photo_enhanced.jpg (in same directory)
```

### Batch Processing

```bash
# Process all photos in a folder
python enhance_portrait.py -d ~/Pictures/portraits/

# Process photos in current directory
python enhance_portrait.py -d .
```

## Troubleshooting

### No face detected

If the script reports "No face detected", it will still process the image but skip face-specific enhancements (local sharpening, skin smoothing, background blur, eye enhancement). This can happen if:
- The image doesn't contain a visible face
- The face is too small or at an extreme angle
- The image has very poor lighting

### Dependencies not found

If you get import errors:
1. Ensure you've activated your virtual environment (if using one)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (must be 3.8+)

### MediaPipe warnings

MediaPipe may show warnings about model loading. These are usually harmless and the script will still work correctly.

## Technical Details

### Supported Image Formats

- **Input**: `.jpg`, `.jpeg`, `.JPG`, `.JPEG`
- **Output**: High-quality JPEG (95% quality setting)

### Performance

- Single image: 2-10 seconds (depending on resolution and hardware)
- Batch processing: Processes images sequentially
- Memory usage: Scales with image resolution

### Image Quality

- Output JPEG quality: 95% (near-lossless)
- All processing done in high precision (float32 when needed)
- Smooth transitions between enhanced regions using Gaussian-blurred masks

## License

This project uses open-source libraries:
- OpenCV (Apache 2.0 License)
- MediaPipe (Apache 2.0 License)
- NumPy (BSD License)
- Pillow (HPND License)

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new enhancement features
- Improve the documentation
- Submit pull requests

## Credits

Developed for CachyOS (Arch-based Linux) using only open-source libraries available via pacman and pip.

**MediaPipe Face Mesh Model**: Google MediaPipe  
**URL**: https://google.github.io/mediapipe/solutions/face_mesh.html
