import argparse
import csv
import os
import re
import shutil
import zipfile
from pathlib import Path
from typing import Dict
from typing import List
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
    if localappdata_path is not None and os.path.exists(Path(localappdata_path) / r'Tesseract-OCR/tesseract.exe'):
        print('Tesseract found at %LocalAppData%/Tesseract-OCR/tesseract.exe, setting as tesseract executable')
        pytesseract.pytesseract.tesseract_cmd = str(Path(localappdata_path) / r'Tesseract-OCR/tesseract.exe')
except ModuleNotFoundError:
    print('Module pillow or pytesseract not found, ocr will not be available for image files')


def main():
    parser = argparse.ArgumentParser(
        prog='Practice-It grader',
        description='Scans a directory of completed Practice-It assignments and records the scores')
    parser.add_argument('submissions', type=str, help='Path to the directory or zip file containing the files to grade')
    parser.add_argument('--questions', type=str, default='questions.txt',
                        help='Path to the file containing the list of questions. Defaults to questions.txt')
    parser.add_argument('--names', type=str, default='names.txt',
                        help='''Path to the file containing the list of student names. Defaults to names.txt.
                                This can be omitted if you are not interested in the paired scores file.''')
    parser.add_argument('--output', type=str, default='scores.csv',
                        help='Path to where the output should be placed. Defaults to scores.csv')
    parser.add_argument('--paired-output', type=str, default='paired_scores.csv',
                        help='''Path to where the output consisting of scores paired to student names should be placed.
                                Defaults to paired_scores.csv.''')
    parser.add_argument('--disable-ocr', action='store_true',
                        help='Disable OCR, even if tesseract is installed')
    args = parser.parse_args()

    if args.disable_ocr:
        global pdf_ocr_available, image_ocr_available
        pdf_ocr_available = False
        image_ocr_available = False

    target_dir: str
    if os.path.isdir(args.submissions):
        target_dir = args.submissions
    elif os.path.isfile(args.submissions) and re.match(r'^.*\.zip$', args.submissions):
        if os.path.exists('temp_extracted_submissions') and os.path.isdir('temp_extracted_submissions'):
            shutil.rmtree('temp_extracted_submissions')
        print(f'Extracting {args.submissions} to "temp_extracted_submissions/"')
        with zipfile.ZipFile(args.submissions, 'r') as zip_ref:
            zip_ref.extractall('temp_extracted_submissions')
        target_dir = 'temp_extracted_submissions'
    else:
        print(f'Directory not found: {args.submissions}')
        raise FileNotFoundError("Directory not found")
    files_in_directory: List[str] = os.listdir(target_dir)

    # Read list of questions from questions.txt
    questions: List[str]
    with open(args.questions, 'r+') as f:
        questions = f.read().splitlines()

    # Create dictionary to store scores in
    data: List[Dict[str, str | int]] = []

    # Scan files
    for file_to_scan in files_in_directory:
        filepath: Path = Path(target_dir) / file_to_scan
        score: int = 0
        missing_questions: List[str] = []
        doc_type: str = 'unknown'

        # Image files
        if image_ocr_available and re.match(r'.*\.(png|jpg)$', file_to_scan):
            print(f'Scanning image with tesseract {filepath}: ', end='')
            img = Image.open(filepath)
            img.convert("1")
            text = pytesseract.image_to_string(img)
            (score, missing_questions) = get_score_and_missing_questions(text, questions)
            doc_type = 'image'
            print(f'{score} pts')

        # PDF files
        if re.match(r'.*\.pdf$', file_to_scan):
            # Scan file
            print(f'Scanning pdf {filepath}: ', end='')
            text = extract_text(str(filepath))
            (score, missing_questions) = get_score_and_missing_questions(text, questions)
            doc_type = 'pdf'
            print(f'{score} pts')

            # If score is 0, rescan file with ocr
            if score == 0 and pdf_ocr_available:
                print(f'Applying OCR to {filepath}...')
                try:
                    ocrmypdf.ocr(str(filepath), 'temp.pdf')  # pyright: ignore[reportPrivateImportUsage]
                    print(f'Rescanning OCR version of {filepath}: ', end='')
                    text = extract_text('temp.pdf')
                    (score, missing_questions) = get_score_and_missing_questions(text, questions)
                    doc_type = 'image pdf'
                    print(f'{score} pts')
                    os.remove('temp.pdf')
                except PriorOcrFoundError:
                    print('OCR failed because text was already present')

        # Store score in dictionary
        student_name: str = file_to_scan.split('_', 1)[0]
        data.append({'student_name': student_name,
                     'score': score,
                     'missing_questions': str(missing_questions),
                     'type': doc_type})

    # Write scores to scores.csv
    with open(args.output, 'w', newline='') as f:
        fieldnames = ['student_name', 'score', 'missing_questions', 'type']
        w = csv.DictWriter(f, fieldnames=fieldnames)

        w.writeheader()
        for entry in data:
            w.writerow(entry)

    # Generate paired_scores.csv
    student_names: List[str]
    try:
        with open(args.names, 'r+') as f:
            student_names = f.read().splitlines()
    except FileNotFoundError:
        print(f'{args.names} not found, will not generate paired score list')
    else:
        paired_scores = pair_scores(data, student_names)
        with open(args.paired_output, 'w', newline='') as f:
            fieldnames = ['true_name', 'student_name', 'score', 'missing_questions', 'type']
            w = csv.DictWriter(f, fieldnames=fieldnames)

            w.writeheader()
            for entry in paired_scores:
                w.writerow(entry)


def get_score_and_missing_questions(text: str, questions: List[str]) -> Tuple[int, List[str]]:
    # Remove duplicate spaces in text
    text = ' '.join(text.split())
    # Count number of completed questions
    completed_questions = 0
    missing_questions: List[str] = []
    for question in questions:
        if len(question) > 0 and (question.strip() in text):
            completed_questions += 1
        elif len(question) > 0:
            missing_questions.append(question)

    return completed_questions, missing_questions


def convert_to_compact_name(name: str) -> str:
    """
    Converts "Doe, Jane" to "doejane". Should work for people with more than two names
    """
    name_without_spaces_or_commas = name.translate(str.maketrans('', '', ', '))
    return name_without_spaces_or_commas.lower()


def pair_scores(score_data: List[Dict[str, str | int]], student_names: List[str]) -> List[Dict[str, str | int]]:
    paired_scores: List[Dict[str, str | int]] = []
    for name in student_names:
        compact_name = convert_to_compact_name(name)
        try:
            first_matching_score = next(score for score in score_data if score['student_name'] == compact_name)
            new_paired_score = first_matching_score.copy()
            new_paired_score['true_name'] = name
            paired_scores.append(new_paired_score)
        except StopIteration:
            new_paired_score = {
                'true_name': name,
                'student_name': '',
                'score': 0,
                'missing_questions': "MISSING",
                'type': ''
            }
            paired_scores.append(new_paired_score)

    # Find scores that did not end up in the "result" list
    for score in score_data:
        if not any(paired_score['student_name'] == score['student_name'] for paired_score in paired_scores):
            new_paired_score = score.copy()
            new_paired_score['true_name'] = '?'
            paired_scores.append(new_paired_score)

    return paired_scores


if __name__ == '__main__':
    main()
