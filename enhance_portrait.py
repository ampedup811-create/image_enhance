#!/usr/bin/env python3
"""
Portrait Image Enhancement Script

This script applies professional-grade enhancements to portrait photographs:
- Auto-crop to remove ceiling lights
- White balance correction
- Contrast enhancement
- Facial feature sharpening (eyes, hair)
- Skin smoothing
- Background blur (depth of field simulation)
- Eye enhancement

Compatible with CachyOS (Arch-based Linux)
Requires: opencv-python, numpy, mediapipe, Pillow
"""

import os
import sys
import argparse
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from typing import Optional, Tuple, List


class PortraitEnhancer:
    """Main class for portrait enhancement operations."""
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh for facial landmark detection."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
    def auto_crop_top(self, image: np.ndarray, crop_percent: float = 0.1) -> np.ndarray:
        """
        Remove a percentage from the top of the image (to eliminate ceiling lights).
        
        Args:
            image: Input image (BGR format)
            crop_percent: Percentage to crop from top (default 0.1 = 10%)
            
        Returns:
            Cropped image
        """
        height = image.shape[0]
        crop_pixels = int(height * crop_percent)
        return image[crop_pixels:, :, :]
    
    def adjust_white_balance(self, image: np.ndarray) -> np.ndarray:
        """
        Adjust white balance to reduce warm (yellow) tones.
        Uses gray world assumption for neutral white point.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            White-balanced image
        """
        # Convert to float for precision
        result = image.copy().astype(np.float32)
        
        # Calculate average for each channel
        avg_b = np.mean(result[:, :, 0])
        avg_g = np.mean(result[:, :, 1])
        avg_r = np.mean(result[:, :, 2])
        
        # Calculate gray world average
        gray_avg = (avg_b + avg_g + avg_r) / 3
        
        # Apply scaling factors to balance channels
        result[:, :, 0] *= gray_avg / avg_b
        result[:, :, 1] *= gray_avg / avg_g
        result[:, :, 2] *= gray_avg / avg_r
        
        # Clip values to valid range and convert back to uint8
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    def increase_contrast(self, image: np.ndarray, alpha: float = 1.2) -> np.ndarray:
        """
        Increase contrast to enhance facial features.
        
        Args:
            image: Input image (BGR format)
            alpha: Contrast control (>1 increases contrast)
            
        Returns:
            Contrast-enhanced image
        """
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Apply additional contrast enhancement
        result = cv2.convertScaleAbs(result, alpha=alpha, beta=0)
        
        return result
    
    def detect_facial_landmarks(self, image: np.ndarray) -> Optional[dict]:
        """
        Detect facial landmarks using MediaPipe Face Mesh.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary with landmark positions or None if no face detected
        """
        # Convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        
        if not results.multi_face_landmarks:
            return None
        
        # Get first face landmarks
        landmarks = results.multi_face_landmarks[0]
        h, w = image.shape[:2]
        
        # Extract key landmark regions
        landmark_dict = {
            'all': [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
        }
        
        # Left eye: landmarks 33, 133, 160, 158, 144, 153
        left_eye_indices = [33, 133, 160, 158, 144, 153, 145, 159]
        landmark_dict['left_eye'] = [
            (int(landmarks.landmark[i].x * w), int(landmarks.landmark[i].y * h))
            for i in left_eye_indices
        ]
        
        # Right eye: landmarks 362, 263, 387, 385, 373, 380
        right_eye_indices = [362, 263, 387, 385, 373, 380, 374, 386]
        landmark_dict['right_eye'] = [
            (int(landmarks.landmark[i].x * w), int(landmarks.landmark[i].y * h))
            for i in right_eye_indices
        ]
        
        # Face contour for hair region (forehead and top)
        forehead_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                           397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                           172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        landmark_dict['hair'] = [
            (int(landmarks.landmark[i].x * w), int(landmarks.landmark[i].y * h))
            for i in forehead_indices
        ]
        
        return landmark_dict
    
    def sharpen_region(self, image: np.ndarray, mask: np.ndarray, amount: float = 1.5) -> np.ndarray:
        """
        Apply sharpening to a specific region defined by a mask.
        
        Args:
            image: Input image (BGR format)
            mask: Binary mask (0-255) defining region to sharpen
            amount: Sharpening intensity
            
        Returns:
            Image with region sharpened
        """
        # Create unsharp mask
        gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
        sharpened = cv2.addWeighted(image, 1.0 + amount, gaussian, -amount, 0)
        
        # Apply sharpening only to masked region
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        result = (image * (1 - mask_3ch) + sharpened * mask_3ch).astype(np.uint8)
        
        return result
    
    def apply_local_sharpening(self, image: np.ndarray, landmarks: Optional[dict]) -> np.ndarray:
        """
        Apply local sharpening to eyes and hair regions.
        
        Args:
            image: Input image (BGR format)
            landmarks: Dictionary with facial landmarks
            
        Returns:
            Image with sharpened features
        """
        if landmarks is None:
            print("  Warning: No face detected, skipping local sharpening")
            return image
        
        result = image.copy()
        h, w = image.shape[:2]
        
        # Create mask for eyes
        eye_mask = np.zeros((h, w), dtype=np.uint8)
        
        # Draw ellipses around eyes
        if 'left_eye' in landmarks and len(landmarks['left_eye']) > 0:
            left_eye_pts = np.array(landmarks['left_eye'], dtype=np.int32)
            x, y, w_eye, h_eye = cv2.boundingRect(left_eye_pts)
            # Expand region slightly
            padding = 15
            x, y = max(0, x - padding), max(0, y - padding)
            w_eye, h_eye = w_eye + 2 * padding, h_eye + 2 * padding
            cv2.ellipse(eye_mask, (x + w_eye // 2, y + h_eye // 2), 
                       (w_eye // 2, h_eye // 2), 0, 0, 360, 255, -1)
        
        if 'right_eye' in landmarks and len(landmarks['right_eye']) > 0:
            right_eye_pts = np.array(landmarks['right_eye'], dtype=np.int32)
            x, y, w_eye, h_eye = cv2.boundingRect(right_eye_pts)
            # Expand region slightly
            padding = 15
            x, y = max(0, x - padding), max(0, y - padding)
            w_eye, h_eye = w_eye + 2 * padding, h_eye + 2 * padding
            cv2.ellipse(eye_mask, (x + w_eye // 2, y + h_eye // 2),
                       (w_eye // 2, h_eye // 2), 0, 0, 360, 255, -1)
        
        # Blur the mask for smooth transition
        eye_mask = cv2.GaussianBlur(eye_mask, (21, 21), 0)
        
        # Apply sharpening to eyes
        result = self.sharpen_region(result, eye_mask, amount=1.8)
        
        # Create mask for hair region (upper part of image)
        hair_mask = np.zeros((h, w), dtype=np.uint8)
        if 'hair' in landmarks and len(landmarks['hair']) > 0:
            hair_pts = np.array(landmarks['hair'], dtype=np.int32)
            hull = cv2.convexHull(hair_pts)
            # Extend upward for hair
            hull_extended = hull.copy()
            hull_extended[:, 0, 1] = np.maximum(0, hull_extended[:, 0, 1] - 80)
            cv2.fillPoly(hair_mask, [hull_extended], 255)
            # Keep only upper portion
            hair_mask[h // 2:, :] = 0
        
        # Blur the mask for smooth transition
        hair_mask = cv2.GaussianBlur(hair_mask, (31, 31), 0)
        
        # Apply sharpening to hair
        result = self.sharpen_region(result, hair_mask, amount=1.2)
        
        return result
    
    def apply_skin_smoothing(self, image: np.ndarray, landmarks: Optional[dict]) -> np.ndarray:
        """
        Apply subtle skin smoothing using bilateral filter.
        
        Args:
            image: Input image (BGR format)
            landmarks: Dictionary with facial landmarks
            
        Returns:
            Image with smoothed skin
        """
        if landmarks is None:
            print("  Warning: No face detected, applying gentle smoothing to entire image")
            # Apply mild smoothing to entire image
            return cv2.bilateralFilter(image, 5, 20, 20)
        
        # Create a mask for the face region
        h, w = image.shape[:2]
        face_mask = np.zeros((h, w), dtype=np.uint8)
        
        if 'all' in landmarks and len(landmarks['all']) > 0:
            # Use convex hull of face landmarks
            face_pts = np.array(landmarks['all'], dtype=np.int32)
            hull = cv2.convexHull(face_pts)
            cv2.fillPoly(face_mask, [hull], 255)
        
        # Apply bilateral filter for skin smoothing (preserves edges)
        smoothed = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Blur the mask for smooth transition
        face_mask_blurred = cv2.GaussianBlur(face_mask, (51, 51), 0)
        face_mask_3ch = cv2.cvtColor(face_mask_blurred, cv2.COLOR_GRAY2BGR) / 255.0
        
        # Blend smoothed and original
        result = (image * (1 - face_mask_3ch * 0.6) + smoothed * face_mask_3ch * 0.6).astype(np.uint8)
        
        return result
    
    def blur_background(self, image: np.ndarray, landmarks: Optional[dict]) -> np.ndarray:
        """
        Darken and blur the background to emphasize the subject.
        Simulates depth of field effect.
        
        Args:
            image: Input image (BGR format)
            landmarks: Dictionary with facial landmarks
            
        Returns:
            Image with blurred background
        """
        if landmarks is None:
            print("  Warning: No face detected, skipping background blur")
            return image
        
        h, w = image.shape[:2]
        
        # Create subject mask (face + surrounding area)
        subject_mask = np.zeros((h, w), dtype=np.uint8)
        
        if 'all' in landmarks and len(landmarks['all']) > 0:
            # Create expanded mask around face
            face_pts = np.array(landmarks['all'], dtype=np.int32)
            hull = cv2.convexHull(face_pts)
            
            # Expand the hull for full subject area (head, shoulders)
            center = hull.mean(axis=0).astype(int)
            expanded_hull = ((hull - center) * 2.5 + center).astype(np.int32)
            cv2.fillPoly(subject_mask, [expanded_hull], 255)
        
        # Apply heavy Gaussian blur to mask for smooth transition
        subject_mask = cv2.GaussianBlur(subject_mask, (99, 99), 0)
        
        # Create blurred and darkened version of image
        blurred = cv2.GaussianBlur(image, (21, 21), 0)
        darkened = cv2.convertScaleAbs(blurred, alpha=0.8, beta=-10)
        
        # Blend based on mask
        subject_mask_3ch = cv2.cvtColor(subject_mask, cv2.COLOR_GRAY2BGR) / 255.0
        result = (image * subject_mask_3ch + darkened * (1 - subject_mask_3ch)).astype(np.uint8)
        
        return result
    
    def enhance_eyes(self, image: np.ndarray, landmarks: Optional[dict]) -> np.ndarray:
        """
        Enhance eye brightness and saturation subtly.
        
        Args:
            image: Input image (BGR format)
            landmarks: Dictionary with facial landmarks
            
        Returns:
            Image with enhanced eyes
        """
        if landmarks is None:
            return image
        
        result = image.copy()
        h, w = image.shape[:2]
        
        # Create mask for both eyes
        eye_mask = np.zeros((h, w), dtype=np.uint8)
        
        for eye_key in ['left_eye', 'right_eye']:
            if eye_key in landmarks and len(landmarks[eye_key]) > 0:
                eye_pts = np.array(landmarks[eye_key], dtype=np.int32)
                cv2.fillPoly(eye_mask, [eye_pts], 255)
        
        # Expand and blur mask for smooth transition
        kernel = np.ones((5, 5), np.uint8)
        eye_mask = cv2.dilate(eye_mask, kernel, iterations=2)
        eye_mask = cv2.GaussianBlur(eye_mask, (15, 15), 0)
        
        # Convert to HSV for saturation and brightness adjustment
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Create enhancement factors
        eye_mask_normalized = eye_mask.astype(np.float32) / 255.0
        
        # Increase brightness (V channel)
        hsv[:, :, 2] = hsv[:, :, 2] * (1 + eye_mask_normalized * 0.15)
        
        # Increase saturation (S channel) slightly
        hsv[:, :, 1] = hsv[:, :, 1] * (1 + eye_mask_normalized * 0.2)
        
        # Clip and convert back
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def enhance_portrait(self, image_path: str, output_path: Optional[str] = None) -> bool:
        """
        Apply all enhancement steps to a portrait image.
        
        Args:
            image_path: Path to input image
            output_path: Path for output image (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Processing: {image_path}")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"  Error: Could not load image from {image_path}")
                return False
            
            print(f"  Original size: {image.shape[1]}x{image.shape[0]}")
            
            # Step 1: Auto-crop top 10%
            print("  Step 1: Auto-cropping top 10%...")
            image = self.auto_crop_top(image, crop_percent=0.1)
            
            # Step 2: Adjust white balance
            print("  Step 2: Adjusting white balance...")
            image = self.adjust_white_balance(image)
            
            # Step 3: Increase contrast
            print("  Step 3: Increasing contrast...")
            image = self.increase_contrast(image, alpha=1.15)
            
            # Step 4: Detect facial landmarks
            print("  Step 4: Detecting facial landmarks...")
            landmarks = self.detect_facial_landmarks(image)
            
            # Step 5: Apply local sharpening to eyes and hair
            print("  Step 5: Sharpening eyes and hair...")
            image = self.apply_local_sharpening(image, landmarks)
            
            # Step 6: Apply skin smoothing
            print("  Step 6: Applying skin smoothing...")
            image = self.apply_skin_smoothing(image, landmarks)
            
            # Step 7: Blur and darken background
            print("  Step 7: Blurring background...")
            image = self.blur_background(image, landmarks)
            
            # Step 8: Enhance eyes
            print("  Step 8: Enhancing eyes...")
            image = self.enhance_eyes(image, landmarks)
            
            # Determine output path
            if output_path is None:
                path_obj = Path(image_path)
                output_path = str(path_obj.parent / f"{path_obj.stem}_enhanced{path_obj.suffix}")
            
            # Save with high quality
            print(f"  Saving to: {output_path}")
            cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print("  ✓ Enhancement complete!")
            
            return True
            
        except Exception as e:
            print(f"  Error processing {image_path}: {str(e)}")
            return False
    
    def batch_process(self, input_dir: str) -> None:
        """
        Process all .jpg files in a directory.
        
        Args:
            input_dir: Directory containing images to process
        """
        input_path = Path(input_dir)
        
        if not input_path.exists() or not input_path.is_dir():
            print(f"Error: '{input_dir}' is not a valid directory")
            return
        
        # Find all .jpg files (case insensitive)
        jpg_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.JPG")) + \
                    list(input_path.glob("*.jpeg")) + list(input_path.glob("*.JPEG"))
        
        # Filter out already enhanced files
        jpg_files = [f for f in jpg_files if '_enhanced' not in f.stem]
        
        if not jpg_files:
            print(f"No .jpg files found in '{input_dir}'")
            return
        
        print(f"\nFound {len(jpg_files)} image(s) to process")
        print("=" * 60)
        
        success_count = 0
        for i, jpg_file in enumerate(jpg_files, 1):
            print(f"\n[{i}/{len(jpg_files)}]")
            if self.enhance_portrait(str(jpg_file)):
                success_count += 1
        
        print("\n" + "=" * 60)
        print(f"Batch processing complete: {success_count}/{len(jpg_files)} images enhanced")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Enhance portrait photographs with professional-grade adjustments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  python enhance_portrait.py portrait.jpg
  
  # Process a single image with custom output path
  python enhance_portrait.py portrait.jpg -o output.jpg
  
  # Batch process all .jpg files in a directory
  python enhance_portrait.py -d /path/to/photos/
  
  # Batch process all .jpg files in current directory
  python enhance_portrait.py -d .

Enhancement steps applied:
  1. Auto-crop top 10% (removes ceiling lights)
  2. White balance adjustment (reduces yellow/warm tones)
  3. Contrast enhancement (emphasizes facial features)
  4. Local sharpening (eyes and hair via facial landmarks)
  5. Skin smoothing (bilateral filter)
  6. Background blur (depth of field simulation)
  7. Eye enhancement (brightness and saturation)
  8. Save as high-quality JPEG with '_enhanced' suffix
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input image file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output image file path (default: adds _enhanced to filename)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Process all .jpg files in the specified directory'
    )
    
    args = parser.parse_args()
    
    # Check if either input file or directory is provided
    if not args.input and not args.directory:
        parser.print_help()
        sys.exit(1)
    
    # Initialize enhancer
    print("Initializing Portrait Enhancer...")
    print("Loading MediaPipe Face Mesh model...")
    enhancer = PortraitEnhancer()
    print("Ready!\n")
    
    # Process based on mode
    if args.directory:
        # Batch mode
        enhancer.batch_process(args.directory)
    else:
        # Single file mode
        if not os.path.exists(args.input):
            print(f"Error: File '{args.input}' not found")
            sys.exit(1)
        
        success = enhancer.enhance_portrait(args.input, args.output)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
