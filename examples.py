#!/usr/bin/env python3
"""
Example: Using PortraitEnhancer programmatically

This script demonstrates how to use the PortraitEnhancer class
in your own Python code.
"""

from enhance_portrait import PortraitEnhancer

def example_single_image():
    """Example: Enhance a single image."""
    print("Example 1: Single Image Enhancement")
    print("-" * 50)
    
    enhancer = PortraitEnhancer()
    success = enhancer.enhance_portrait("my_photo.jpg")
    
    if success:
        print("✓ Image enhanced successfully!")
    else:
        print("✗ Enhancement failed")
    print()


def example_batch_processing():
    """Example: Batch process a directory."""
    print("Example 2: Batch Processing")
    print("-" * 50)
    
    enhancer = PortraitEnhancer()
    enhancer.batch_process("./photos")
    print()


def example_custom_output():
    """Example: Specify custom output path."""
    print("Example 3: Custom Output Path")
    print("-" * 50)
    
    enhancer = PortraitEnhancer()
    success = enhancer.enhance_portrait(
        image_path="input.jpg",
        output_path="output/enhanced_portrait.jpg"
    )
    
    if success:
        print("✓ Image saved to custom location!")
    print()


def example_multiple_images():
    """Example: Process multiple specific images."""
    print("Example 4: Process Multiple Specific Images")
    print("-" * 50)
    
    enhancer = PortraitEnhancer()
    
    image_list = [
        "portrait1.jpg",
        "portrait2.jpg",
        "portrait3.jpg"
    ]
    
    for image_path in image_list:
        print(f"Processing {image_path}...")
        enhancer.enhance_portrait(image_path)
    print()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Portrait Enhancement Examples")
    print("=" * 50 + "\n")
    
    # Uncomment the example you want to run:
    
    # example_single_image()
    # example_batch_processing()
    # example_custom_output()
    # example_multiple_images()
    
    print("\nTo use these examples:")
    print("1. Uncomment the example you want to run")
    print("2. Update the file paths to match your images")
    print("3. Run: python examples.py")
