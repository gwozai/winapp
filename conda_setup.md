# Conda Environment Setup

This document describes how to set up the Python environment for the winapp project using Conda.

## Prerequisites

- Anaconda or Miniconda installed on your system
- Git (for cloning the repository)

## Environment Setup Steps

1. Create a new conda environment with Python 3.8:
```bash
conda create -n winapp python=3.8
```

2. Activate the environment:
```bash
conda activate winapp
```

3. Install project dependencies:
```bash
pip install -r requirements.txt
```

## Project Dependencies

The project requires the following packages (as specified in requirements.txt):
- PyQt5 5.15.9
- Pillow
- PyInstaller
- Redis
- Requests
- Minio

## Running the Application

After setting up the environment, you can run the application using:
```bash
python main.py
```

## Notes

- Make sure to always activate the conda environment before working on the project
- If you add new dependencies, remember to update requirements.txt
- The environment name 'winapp' matches the project name for consistency 