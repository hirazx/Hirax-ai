from setuptools import setup, find_packages

setup(
    name="hirax-ai",
    version="2.0.0",
    description="Hirax AI - Offline AI Developer Assistant",
    author="Hirax Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "websockets",
        "aiofiles",
        "python-dotenv",
        "llama-cpp-python",
        "pypdf2",
        "pytesseract",
        "Pillow",
    ],
    entry_points={
        'console_scripts': [
            'hirax=backend.main:run_server',
        ],
    },
)