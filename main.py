import os
import sys
import re
import csv
from PIL import Image
from pathlib import Path
from typing import List
from typing import Dict

from ocrmypdf.exceptions import PriorOcrFoundError
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/Niels/AppData/Local/Tesseract-OCR/tesseract.exe'

try:
    from pdfminer.high_level import extract_text
except ImportError:
    print('Module pdfminer not found, is pdfminer.six installed?')
    exit(1)

ocr_avaliable: bool = False
try:
    import ocrmypdf
    ocr_available = True
except ImportError:
    print('Module ocrmypdf not found, ocr will not be available for pdfs')

def main():
    # Get list of files to scan
    if len(sys.argv) != 2:
        print('Exactly one command line argument should be supplied');
        exit(1)
    files_in_directory: List[str] = os.listdir(sys.argv[1])

    # Read list of questions from questions.txt
    questions: List[str]
    with open('questions.txt', 'r+') as f:
        questions = f.read().splitlines()

    # Create dictionary to store scores in
    scores: Dict[str, int] = {}

    # Scan files
    for file_to_scan in files_in_directory:
        filepath: Path = Path(sys.argv[1]) / file_to_scan

        # Image files
        if re.match(r'.*\.(png|jpg)$', file_to_scan):
            print(f'Scanning image with tesseract {filepath}: ', end='')
            text = pytesseract.image_to_string(Image.open(filepath))
            score: int = get_score(text, questions)
            print(f'{score} pts')

        # PDF files
        if re.match(r'.*\.pdf$', file_to_scan):
            # Scan file
            print(f'Scanning pdf {filepath}: ', end='')
            text = extract_text(str(filepath))
            score: int = get_score(text, questions)
            print(f'{score} pts')

            # If score is 0, rescan file with ocr
            if score == 0:
                print(f'Applying ocr to {filepath}...')
                try:
                    ocrmypdf.ocr(str(filepath), 'temp.pdf')
                    print(f'Rescanning ocr version of {filepath}: ')
                    text = extract_text('temp.pdf')
                    score = get_score(text, questions)
                    print(f'{score} pts')
                    os.remove('temp.pdf')
                except PriorOcrFoundError:
                    print('OCR failed because text was already present')

            # Store score in dictionary
            studentname: str = file_to_scan.split('_', 1)[0]
            scores[studentname] = score

    # Write scores to scores.csv
    with open('scores.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerows(scores.items())

def get_score(text: str, questions: List[str]) -> int:
    # Remove duplicate spaces in text
    text = ' '.join(text.split())

    # Count number of completed questions
    completed_questions = 0
    for question in questions:
        if len(question) > 0 and question in text != -1:
            completed_questions += 1

    return completed_questions

if __name__ == '__main__':
    main()
