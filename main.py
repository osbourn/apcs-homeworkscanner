import os
import sys
import re
import csv
from pathlib import Path
from typing import List
from typing import Dict

from pdfminer.high_level import extract_text

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
        if re.match(r'.*\.pdf$', file_to_scan):
            # Scan file
            filepath: Path = Path(sys.argv[1]) / file_to_scan
            score: int = get_score(filepath, questions)

            # Store score in dictionary
            studentname: str = file_to_scan.split('_', 1)[0]
            scores[studentname] = score

    # Write scores to scores.csv
    with open('scores.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerows(scores.items())

def get_score(filepath: Path, questions: List[str]) -> int:
    # Get text from file
    print(f'Scanning pdf {filepath}: ', end='')
    text = extract_text(str(filepath))

    # Remove duplicate spaces in text
    text = ' '.join(text.split())

    # Count number of completed questions
    completed_questions = 0
    for question in questions:
        if len(question) > 0 and question in text != -1:
            completed_questions += 1
    print(f'{completed_questions} pts')

    return completed_questions

if __name__ == '__main__':
    main()
