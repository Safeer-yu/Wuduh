# Wuduh
## UAE Legal Assistant
Building a RAG tool that will help people in the uae clarify labor rules


## Environment Setup
- **Operating System:** Windows 11 with WSL2 (Ubuntu)
- **Editor:** VS Code with WSL Extension
- **Git:** Configured within the Ubuntu terminal

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Installation
### Install required packages 
```bash 
pip install -r requirements.txt
```

## Arabic OCR Dependencies (Ubuntu/WSL)

Run this once before using the Arabic text extractor:

```bash
# Fix any broken packages first (important on Ubuntu/WSL)
sudo apt-get update
sudo apt-get install -f
sudo dpkg --configure -a

# System dependencies
sudo apt-get install libarchive13t64 poppler-utils tesseract-ocr tesseract-ocr-ara

# Python dependencies
pip install pytesseract Pillow
```

### Copy the template file to create your own 
`.env` file:
   ```bash
   cp .env.example .env
   ```


## activate environment
``` bash
conda activate wuduh-env
```

## Running the Application
``` bash
streamlit run src/app.py
```
