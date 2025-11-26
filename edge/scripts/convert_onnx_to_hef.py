#!/usr/bin/env python3
"""
Convert ONNX model to Hailo HEF format for Hailo-8L acceleration

Requirements:
- Hailo Dataflow Compiler (DFC) installed
- hailo_sdk_client package

Usage:
    python convert_onnx_to_hef.py \
        --input model.onnx \
        --output model.hef \
        --calib-dataset /path/to/calibration/images \
        --batch-size 1

Installation:
    Follow Hailo documentation for installing DFC:
    https://hailo.ai/developer-zone/documentation/dataflow-compiler/
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_hailo_sdk():
    """Check if Hailo SDK is available"""
    try:
        from hailo_sdk_client import ClientRunner
        logger.info("Hailo SDK client found")
        return True
    except ImportError:
        logger.error("Hailo SDK not found. Please install it first:")
        logger.error("  Follow: https://hailo.ai/developer-zone/documentation/")
        return False


def convert_onnx_to_hef(
    onnx_path: Path,
    hef_path: Path,
    calib_dataset: Optional[Path] = None,
    batch_size: int = 1,
    target_device: str = "hailo8l",
    optimization_level: int = 2,
    precision: str = "int8",
) -> bool:
    """
    Convert ONNX model to HEF format

    Args:
        onnx_path: Path to input ONNX model
        hef_path: Path to output HEF file
        calib_dataset: Path to calibration dataset (required for quantization)
        batch_size: Model batch size
        target_device: Target Hailo device (hailo8, hailo8l)
        optimization_level: Optimization level (0-4)
        precision: Model precision (int8, mixed)

    Returns:
        True if conversion successful, False otherwise
    """
    try:
        from hailo_sdk_client import ClientRunner, InferenceContext
        from hailo_sdk_client.exposed_definitions import States

        logger.info(f"Converting ONNX model: {onnx_path}")
        logger.info(f"Target device: {target_device}")
        logger.info(f"Precision: {precision}")
        logger.info(f"Optimization level: {optimization_level}")

        # Initialize Hailo SDK client
        runner = ClientRunner(hw_arch=target_device)

        # Step 1: Parse ONNX model
        logger.info("Step 1/5: Parsing ONNX model...")
        hn_model, _ = runner.translate_onnx_model(
            str(onnx_path),
            net_name="fast_plate_ocr",
            start_node_names=None,
            end_node_names=None,
            net_input_shapes=None,
        )
        logger.info("✓ Model parsed successfully")

        # Step 2: Optimize model
        logger.info("Step 2/5: Optimizing model...")
        runner.optimize(hn_model)
        logger.info("✓ Model optimized")

        # Step 3: Quantization
        if precision == "int8":
            logger.info("Step 3/5: Quantizing model to INT8...")

            if not calib_dataset or not calib_dataset.exists():
                logger.error("Calibration dataset is required for INT8 quantization")
                logger.error("Provide --calib-dataset with representative images")
                return False

            # Create calibration dataset
            logger.info(f"Loading calibration data from: {calib_dataset}")

            # Quantize model
            quantization_params = {
                'calib_path': str(calib_dataset),
                'batch_size': batch_size,
                'normalize_images': True,
                'resize_images': True,
                'target_shape': (64, 128, 3),  # Height, Width, Channels
            }

            runner.quantize(
                hn_model,
                dataset_path=str(calib_dataset),
                **quantization_params
            )
            logger.info("✓ Model quantized to INT8")
        else:
            logger.info("Step 3/5: Skipping quantization (using mixed precision)")

        # Step 4: Compile to HEF
        logger.info("Step 4/5: Compiling model to HEF format...")

        compile_options = {
            'allocator_script_filename': None,
            'har_path': None,
        }

        hef_binary = runner.compile(
            hn_model,
            hw_arch=target_device,
            **compile_options
        )

        logger.info("✓ Model compiled to HEF")

        # Step 5: Save HEF file
        logger.info(f"Step 5/5: Saving HEF file to: {hef_path}")
        hef_path.parent.mkdir(parents=True, exist_ok=True)

        with open(hef_path, 'wb') as f:
            f.write(hef_binary)

        logger.info("✓ HEF file saved successfully")

        # Print model info
        logger.info("\n" + "="*50)
        logger.info("Conversion completed successfully!")
        logger.info(f"Input:  {onnx_path}")
        logger.info(f"Output: {hef_path}")
        logger.info(f"Size:   {hef_path.stat().st_size / 1024 / 1024:.2f} MB")
        logger.info("="*50)

        return True

    except ImportError as e:
        logger.error(f"Failed to import Hailo SDK: {e}")
        logger.error("Please install Hailo SDK first:")
        logger.error("  pip install hailo-sdk-client")
        return False

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_calibration_dataset_info(dataset_path: Path):
    """
    Create instructions for calibration dataset

    Args:
        dataset_path: Path where calibration dataset should be placed
    """
    logger.info("\n" + "="*70)
    logger.info("CALIBRATION DATASET REQUIRED")
    logger.info("="*70)
    logger.info("\nFor INT8 quantization, you need representative images.")
    logger.info("These should be license plate crops similar to what the model")
    logger.info("will see in production.\n")
    logger.info("Recommended dataset structure:")
    logger.info(f"  {dataset_path}/")
    logger.info("    ├── plate_001.jpg")
    logger.info("    ├── plate_002.jpg")
    logger.info("    ├── plate_003.jpg")
    logger.info("    └── ...")
    logger.info("\nRecommendations:")
    logger.info("  - 100-500 representative images")
    logger.info("  - Variety of lighting conditions")
    logger.info("  - Different plate styles and angles")
    logger.info("  - Clean, centered plate crops")
    logger.info("\nYou can extract plates from your cameras using:")
    logger.info("  python extract_plates_for_calibration.py")
    logger.info("="*70 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert ONNX model to Hailo HEF format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert with INT8 quantization (recommended)
  python convert_onnx_to_hef.py \\
      --input model.onnx \\
      --output model.hef \\
      --calib-dataset /path/to/calibration/images \\
      --batch-size 1 \\
      --target hailo8l

  # Convert without quantization (lower performance)
  python convert_onnx_to_hef.py \\
      --input model.onnx \\
      --output model.hef \\
      --precision mixed \\
      --target hailo8l

For more info: https://hailo.ai/developer-zone/documentation/
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help='Path to input ONNX model'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Path to output HEF file'
    )
    parser.add_argument(
        '--calib-dataset', '-c',
        type=Path,
        default=None,
        help='Path to calibration dataset (required for INT8 quantization)'
    )
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=1,
        help='Model batch size (default: 1)'
    )
    parser.add_argument(
        '--target', '-t',
        type=str,
        default='hailo8l',
        choices=['hailo8', 'hailo8l'],
        help='Target Hailo device (default: hailo8l)'
    )
    parser.add_argument(
        '--precision', '-p',
        type=str,
        default='int8',
        choices=['int8', 'mixed'],
        help='Model precision (default: int8)'
    )
    parser.add_argument(
        '--optimization-level',
        type=int,
        default=2,
        choices=[0, 1, 2, 3, 4],
        help='Optimization level 0-4 (default: 2)'
    )

    args = parser.parse_args()

    # Check if Hailo SDK is available
    if not check_hailo_sdk():
        sys.exit(1)

    # Validate input file
    if not args.input.exists():
        logger.error(f"Input ONNX file not found: {args.input}")
        sys.exit(1)

    # Check calibration dataset
    if args.precision == 'int8':
        if not args.calib_dataset:
            logger.error("--calib-dataset is required for INT8 precision")
            create_calibration_dataset_info(Path("./calibration_data"))
            sys.exit(1)

        if not args.calib_dataset.exists():
            logger.error(f"Calibration dataset not found: {args.calib_dataset}")
            create_calibration_dataset_info(args.calib_dataset)
            sys.exit(1)

    # Perform conversion
    success = convert_onnx_to_hef(
        onnx_path=args.input,
        hef_path=args.output,
        calib_dataset=args.calib_dataset,
        batch_size=args.batch_size,
        target_device=args.target,
        optimization_level=args.optimization_level,
        precision=args.precision,
    )

    if success:
        logger.info("\n✓ Conversion completed successfully!")
        logger.info(f"HEF file ready: {args.output}")
        logger.info("\nYou can now use this model in your edge worker config:")
        logger.info("  ocr:")
        logger.info("    models:")
        logger.info("      - engine: fast_plate_ocr")
        logger.info(f"        model_path: {args.output}")
        logger.info("        use_hailo: true")
        sys.exit(0)
    else:
        logger.error("\n✗ Conversion failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
