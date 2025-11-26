"""
Edge Worker Setup
ANPR License Plate Recognition System - Edge Computing Component
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="anpr-edge-worker",
    version="0.1.0",
    author="ANPR Team",
    author_email="team@anpr.local",
    description="Edge computing worker for ANPR license plate recognition system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/anpr-edge-worker",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0,<2.0.0",
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "pyyaml>=6.0",
        "PyGObject>=3.44.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "ultralytics>=8.0.0",
        "paddleocr>=2.7.0",
        "easyocr>=1.7.0",
        "pytesseract>=0.3.10",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "requests>=2.31.0",
        "websocket-client>=1.6.0",
        "aiohttp>=3.8.5",
        "paho-mqtt>=1.6.1",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "loguru>=0.7.0",
        "prometheus-client>=0.17.0",
        "diskcache>=5.6.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "tensorflow": [
            "tensorflow>=2.13.0,<3.0.0",
        ],
        "onnx": [
            "onnxruntime>=1.15.0",
        ],
        "all": [
            "tensorflow>=2.13.0,<3.0.0",
            "onnxruntime>=1.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "anpr-edge=edge.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "edge": ["config/*.yaml"],
    },
    zip_safe=False,
)
