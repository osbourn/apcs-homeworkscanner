import os
import sys
import re
import csv
from pathlib import Path
from typing import List
from typing import Dict
from typing import Tuple

try:
    from pdfminer.high_level import extract_text
except ModuleNotFoundError:
    print('Module pdfminer not found, is pdfminer.six installed?')
    exit(1)

pdf_ocr_available = False
try:
    import ocrmypdf
    from ocrmypdf.exceptions import PriorOcrFoundError
    pdf_ocr_available = True
except ModuleNotFoundError:
    print('Module ocrmypdf not found, ocr will not be available for pdfs')

image_ocr_available = False
try:
    import pytesseract
    from PIL import Image
    image_ocr_available = True

    # Set location of tesseract on Windows systems that might not have it in PATH
    localappdata_path = os.environ.get('LOCALAPPDATA')
    if localappdata_path != None and os.path.exists(Path(localappdata_path) / r'Tesseract-OCR/tesseract.exe'):
        print('Tesseract found at %LocalAppData%/Tesseract-OCR/tesseract.exe, setting as tesseract executable')
        pytesseract.pytesseract.tesseract_cmd = str(Path(localappdata_path) / r'Tesseract-OCR/tesseract.exe')
except ModuleNotFoundError:
    print('Module pillow or pytesseract not found, ocr will not be available for image files')

def main():
    # Get list of files to scan
    if len(sys.argv) != 2:
        print('Exactly one command line argument should be supplied')
        exit(1)
    files_in_directory: List[str] = os.listdir(sys.argv[1])

    # Read list of questions from questions.txt
    questions: List[str]
    with open('questions.txt', 'r+') as f:
        questions = f.read().splitlines()

    # Create dictionary to store scores in
    data: List[Dict[str, str | int]] = []

    # Scan files
    for file_to_scan in files_in_directory:
        filepath: Path = Path(sys.argv[1]) / file_to_scan
        score: int = 0
        missing_questions: List[str] = []

        # Image files
        if image_ocr_available and re.match(r'.*\.(png|jpg)$', file_to_scan):
            print(f'Scanning image with tesseract {filepath}: ', end='')
            img = Image.open(filepath)
            img.convert("1")
            text = pytesseract.image_to_string(img)
            (score, missing_questions) = get_score_and_missing_questions(text, questions)
            print(f'{score} pts')

        # PDF files
        if re.match(r'.*\.pdf$', file_to_scan):
            # Scan file
            print(f'Scanning pdf {filepath}: ', end='')
            text = extract_text(str(filepath))
            (score, missing_questions) = get_score_and_missing_questions(text, questions)
            print(f'{score} pts')

            # If score is 0, rescan file with ocr
            if score == 0 and pdf_ocr_available:
                print(f'Applying OCR to {filepath}...')
                try:
                    ocrmypdf.ocr(str(filepath), 'temp.pdf') # pyright: ignore[reportPrivateImportUsage]
                    print(f'Rescanning OCR version of {filepath}: ', end='')
                    text = extract_text('temp.pdf')
                    (score, missing_questions) = get_score_and_missing_questions(text, questions)
                    print(f'{score} pts')
                    os.remove('temp.pdf')
                except PriorOcrFoundError:
                    print('OCR failed because text was already present')

        # Store score in dictionary
        studentname: str = file_to_scan.split('_', 1)[0]
        data.append({'student_name': studentname,
                     'score': score,
                     'missing_questions': str(missing_questions)})

    # Write scores to scores.csv
    with open('scores.csv', 'w', newline='') as f:
        fieldnames = ['student_name', 'score', 'missing_questions']
        w = csv.DictWriter(f, fieldnames=fieldnames)

        w.writeheader()
        for entry in data:
            w.writerow(entry)

def get_score_and_missing_questions(text: str, questions: List[str]) -> Tuple[int, List[str]]:
    # Remove duplicate spaces in text
    text = ' '.join(text.split())
    # Count number of completed questions
    completed_questions = 0
    missing_questions: List[str] = []
    for question in questions:
        if len(question) > 0 and (question in text):
            completed_questions += 1
        elif len(question) > 0:
            missing_questions.append(question)

    return (completed_questions, missing_questions)

if __name__ == '__main__':
    main()
