# Table Extraction Engine

A production-grade Python project for extracting tables from **PDF documents** and **images** using **OpenCV**, **Tesseract OCR**, and **Pandas**.

This engine automatically:
- Detects tables
- Segments rows and columns
- Extracts text using OCR
- Converts tables into structured DataFrames
- Exports results to Excel

---

# Features

✅ PDF table extraction  
✅ Image table extraction  
✅ Multi-page PDF support  
✅ Automatic table detection  
✅ OCR-based cell extraction  
✅ Excel export support  
✅ Multiple table handling  
✅ Modular & extensible architecture  
✅ Debug-friendly pipeline

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| OpenCV | Image processing |
| Tesseract OCR | Text recognition |
| pdf2image | PDF → Image conversion |
| Pandas | Structured data handling |
| OpenPyXL | Excel export |
| NumPy | Numerical operations |
| Matplotlib | Visualization/debugging |

---

# Project Workflow

```text
PDF/Image Input
        ↓
Image Loading
        ↓
Table Detection
        ↓
Cell Segmentation
        ↓
OCR Extraction
        ↓
DataFrame Creation
        ↓
Excel Export
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/table-extraction-engine.git

cd table-extraction-engine
```

---

# 2. Install Dependencies

## Linux / Ubuntu / Google Colab

### Install System Packages

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr
```

### Install Python Packages

```bash
pip install opencv-python numpy pandas matplotlib pytesseract pdf2image openpyxl pillow
```

---

# Windows Installation

## Install Tesseract OCR

### Download

Download installer:

https://github.com/UB-Mannheim/tesseract/wiki

Recommended installer:

```text
tesseract-ocr-w64-setup.exe
```

---

## Install Steps

1. Run installer
2. Enable:
   - Add Tesseract to PATH
3. Complete installation

Default path:

```text
C:\Program Files\Tesseract-OCR\
```

---

## Verify Installation

```bash
tesseract --version
```

---

# Install Poppler

## Download

https://github.com/oschwartz10612/poppler-windows/releases

Download latest ZIP release.

---

## Extract

Extract to:

```text
C:\poppler
```

---

## Add to PATH

Add this path to Windows Environment Variables:

```text
C:\poppler\Library\bin
```

---

## Verify Installation

```bash
pdfinfo -v
```

---

# Install Python Packages

```bash
pip install opencv-python numpy pandas matplotlib pytesseract pdf2image openpyxl pillow
```

---

# Important for Windows Users

If Tesseract is not detected automatically:

```python
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
```

---

# If Poppler Path Is Not Detected

```python
from pdf2image import convert_from_path

pages = convert_from_path(
    "sample.pdf",
    poppler_path=r"C:\poppler\Library\bin"
)
```

---

# requirements.txt

Create a `requirements.txt` file:

```txt
opencv-python
numpy
pandas
matplotlib
pytesseract
pdf2image
openpyxl
pillow
```

---

# Usage

## Import

```python
from table_extractor import TableExtractor
```

---

## Extract Tables from PDF

```python
extractor = TableExtractor()

tables = extractor.run("Merged_Cell_Table.pdf")

extractor.export_excel(
    tables,
    "output.xlsx"
)
```

---

## Extract Tables from Image

```python
extractor = TableExtractor()

tables = extractor.run("table.jpg")

extractor.export_excel(
    tables,
    "output.xlsx"
)
```

---

# Example Output

```text
output.xlsx
│
├── Table_1
├── Table_2
└── Table_3
```

Each detected table is exported as a separate Excel sheet.

---

# Folder Structure

```text
table-extraction-engine/
│
├── debug_output/
│   ├── pages/
│   ├── tables/
│   └── cells/
│
├── table_extractor.py
├── requirements.txt
└── README.md
```

---

# Core Functions

## `load_input()`

Loads:
- PDFs
- Images

Returns:

```python
List[np.ndarray]
```

---

## `detect_tables()`

Detects tables using:
- Morphological operations
- Horizontal/vertical line detection
- Contour extraction

---

## `process_table()`

Processes tables into structured rows and columns.

Pipeline:
1. Grid extraction
2. Cell detection
3. Row grouping
4. Column mapping
5. OCR extraction

---

## `preprocess_cell()`

Improves OCR quality using:
- Grayscale conversion
- Resizing
- Gaussian blur
- Otsu thresholding
- Padding

---

## `export_excel()`

Exports extracted tables into:

```text
.xlsx
```

Each table becomes a separate sheet.

---

# OCR Configuration

Current OCR configuration:

```python
config="--oem 3 --psm 6"
```

Example customization:

```python
pytesseract.image_to_string(
    image,
    lang="eng",
    config="--oem 3 --psm 6"
)
```

---

# Google Colab Setup

```python
%%capture

!apt-get update
!apt-get install -y poppler-utils tesseract-ocr

!pip install \
opencv-python \
numpy \
pandas \
matplotlib \
pytesseract \
pdf2image \
openpyxl \
pillow
```

---

# Debug Output

The engine automatically creates:

```text
debug_output/
```

Contains:
- PDF pages
- Detected tables
- Extracted cells

Useful for debugging OCR and table detection.

---

# Performance Tips

Best results with:
- High-resolution scans
- Clear table borders
- Printed text
- Non-rotated tables

---

# Limitations

⚠ Complex merged cells may require custom handling  
⚠ Rotated tables are not fully supported  
⚠ Handwritten tables are not optimized  
⚠ Poor image quality reduces OCR accuracy

---

# Future Improvements

- Deep learning-based table detection
- Streamlit web app
- CSV export
- Multi-language OCR
- Rotated table correction
- Docker support
- API deployment

---

# Common Errors

## `TesseractNotFoundError`

Fix:
- Verify Tesseract installation
- Add Tesseract to PATH
- Restart terminal/IDE

---

## `Unable to get page count`

Fix:
- Verify Poppler installation
- Ensure Poppler is added to PATH

---

# Test Installation

```python
import pytesseract
from pdf2image import convert_from_path

print("Tesseract Installed")
print("Poppler Installed")
```

If no errors occur, setup is complete ✅

---

# License

MIT License

---

# Acknowledgements

- OpenCV
- Tesseract OCR
- Pandas
- pdf2image

---

# Support

If this project helped you, consider giving it a ⭐ on GitHub.
