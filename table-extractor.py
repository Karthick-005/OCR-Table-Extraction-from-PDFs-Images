import os
import cv2
import numpy as np
import pandas as pd
import pytesseract
import matplotlib.pyplot as plt

from typing import List, Tuple, Optional, Union
from pdf2image import convert_from_path


class TableExtractor:
    """
    Production-grade table extraction engine.

    Supports:
        - PDF files (multi-page)
        - Image files (jpg, png, etc.)

    Pipeline:
        Input → Image(s) → Table detection → Cell extraction → OCR → DataFrame
    """

    def __init__(
        self,
        output_dir: str = "debug_output",
        dpi: int = 300
    ) -> None:

        self.output_dir = output_dir
        self.dpi = dpi

        self.page_dir = os.path.join(output_dir, "pages")
        self.table_dir = os.path.join(output_dir, "tables")
        self.cell_dir = os.path.join(output_dir, "cells")

        os.makedirs(self.page_dir, exist_ok=True)
        os.makedirs(self.table_dir, exist_ok=True)
        os.makedirs(self.cell_dir, exist_ok=True)

    # =========================================================
    # IMAGE DISPLAY (DEBUG)
    # =========================================================

    def show(self, title: str, image: np.ndarray) -> None:
        plt.figure(figsize=(10, 6))

        if len(image.shape) == 2:
            plt.imshow(image, cmap="gray")
        else:
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        plt.title(title)
        plt.axis("off")
        plt.show()

    # =========================================================
    # INPUT HANDLER (NEW FEATURE 🔥)
    # =========================================================

    def load_input(self, path: str) -> List[np.ndarray]:
        """
        Load input file (PDF or image) and return list of images.
        """

        ext = os.path.splitext(path)[1].lower()

        images: List[np.ndarray] = []

        if ext == ".pdf":

            pages = convert_from_path(path, dpi=self.dpi)

            for i, page in enumerate(pages):

                page_path = os.path.join(self.page_dir, f"page_{i+1}.png")
                page.save(page_path, "PNG")

                img = cv2.imread(page_path)
                images.append(img)

        else:
            # image input
            img = cv2.imread(path)

            if img is None:
                raise ValueError(f"Cannot read image: {path}")

            images.append(img)

        return images

    # =========================================================
    # PREPROCESS CELL
    # =========================================================

    def preprocess_cell(self, img: np.ndarray) -> np.ndarray:

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        th = cv2.copyMakeBorder(th, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)

        return th

    # =========================================================
    # TABLE DETECTION
    # =========================================================

    def detect_tables(self, image: np.ndarray) -> List[np.ndarray]:

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1]

        horizontal = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (80, 1)),
            iterations=2
        )

        vertical = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (1, 80)),
            iterations=2
        )

        table_mask = cv2.add(horizontal, vertical)

        contours, _ = cv2.findContours(
            table_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        tables = []

        for c in contours:

            x, y, w, h = cv2.boundingRect(c)

            if w > 200 and h > 100:

                tables.append(image[y:y+h, x:x+w])

        return tables

    # =========================================================
    # PROCESS TABLE
    # =========================================================

    def process_table(self, image: np.ndarray) -> List[List[Optional[str]]]:

        original = image.copy()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)[1]

        vertical = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40)),
            iterations=2
        )

        horizontal = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1)),
            iterations=2
        )

        grid = cv2.add(vertical, horizontal)

        contours, _ = cv2.findContours(
            grid,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        cells = []

        img_area = image.shape[0] * image.shape[1]

        for c in contours:

            x, y, w, h = cv2.boundingRect(c)

            if w * h > img_area * 0.8:
                continue

            if w > 40 and h > 20:
                cells.append((x, y, w, h))

        # =====================================================
        # ROW GROUPING
        # =====================================================

        rows = []
        current = []
        prev_y = -1
        tol = 15

        for cell in cells:

            x, y, w, h = cell

            if prev_y == -1:
                prev_y = y

            if abs(y - prev_y) > tol:
                rows.append(current)
                current = []

            current.append(cell)
            prev_y = y

        if current:
            rows.append(current)

        # =====================================================
        # COLUMN DETECTION
        # =====================================================

        all_cells = [c for r in rows for c in r]

        column_centers = []

        for x, y, w, h in sorted(all_cells, key=lambda b: b[0]):

            cx = x + w // 2

            if not any(abs(cx - c) < 10 for c in column_centers):
                column_centers.append(cx)

        column_centers.sort()

        num_cols = len(column_centers)

        # =====================================================
        # OCR + MAPPING
        # =====================================================

        final_data = []

        for row in rows:

            row_data = [None] * num_cols

            for x, y, w, h in row:

                crop = original[y+5:y+h-5, x+5:x+w-5]
                processed = self.preprocess_cell(crop)

                text = pytesseract.image_to_string(
                    processed,
                    config="--oem 3 --psm 6"
                ).strip()

                if text == "":
                    text = None

                cx = x + w // 2

                col_idx = int(np.argmin([
                    abs(cx - c) for c in column_centers
                ]))

                row_data[col_idx] = text

            final_data.append(row_data)

        return final_data

    # =========================================================
    # MAIN PIPELINE (NEW UNIVERSAL ENTRY 🔥)
    # =========================================================

    def run(self, input_path: str) -> List[pd.DataFrame]:
        """
        Run full pipeline for PDF or image input.
        """

        images = self.load_input(input_path)

        all_tables = []

        for img in images:

            tables = self.detect_tables(img)

            for table in tables:

                data = self.process_table(table)

                df = pd.DataFrame(data)

                all_tables.append(df)

        return all_tables

    # =========================================================
    # EXPORT
    # =========================================================

    def export_excel(self, dfs: List[pd.DataFrame], output_path: str) -> None:

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

            for i, df in enumerate(dfs):
                df.to_excel(writer, sheet_name=f"Table_{i+1}", index=False)


extractor = TableExtractor()
tables = extractor.run("/content/Merged_Cell_Table.pdf")
extractor.export_excel(tables, "output.xlsx")

extractor = TableExtractor()
tables = extractor.run("/content/table.jpg")
extractor.export_excel(tables, "output.xlsx")
