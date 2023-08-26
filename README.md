# AP Computer Science - Practice-It Homework Grader

Grades a directory full of screenshots or pdfs of the Practice-It "Problems Solved" page.
It is assumed that the directory contains `.pdf`, `.png`, and `.jpg` named like "lastnamefirstname_something.pdf",
as is the case when the files are submitted on Canvas.

Python is required. I used Python `3.10.6` to test but it likely works on newer version and probably on some older
versions as well.

## Installing requirements

It is recommended to make sure `pip` is up-to-date, otherwise installation of more complex packages (i.e. those
with native code) might fail.

### Base requirements

You need to have these installed to run the script.

```bash
python -m pip install pdfminer.six
```

This script has been tested with `pdfminer.six` version `20221105`.

### Recommended requirements

Without these requirements, image pdfs, jpeg files, and png files will appear to be missing or appear to have no
questions completed.

```bash
python -m pip install ocrmypdf
python -m pip install Pillow
python -m pip install pytesseract
```

You also need to install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and make sure `tesseract` is either
available in `$PATH` or is specifically located at `C:\Users\yourname\AppData\Local\Tesseract-OCR\tesseract.exe` on
Windows.

This script has been tested with `ocrmypdf` version `14.4.0`, `Pillow` version `10.0.0`, and `pytesseract` version
`0.3.10`. `Tesseract OCR` was tested with version `v5.2.0.20220712`.

## Usage

Do the following from the directory containing this `README.md` file:

Create a file named `questions.txt`. Inside it, put one question per line. For example, `question.txt` might look like:
```
Self-Check 1.08
Self-Check 1.14
Self-Check 1.16
Self-Check 1.18
Exercise 1.03
```

These are the strings that will be checked for inside the submissions. Make sure that you enter them exactly as they
would appear in a submission (so put `Self-Check 1.08` and not `Self-Check 1.8`).

You can also run `python translate.py 'SC 1.8, 1.14, 1.16, 1.18, Ex 1.3'` to generate `questions.txt` automatically.

Then create a file named `names.txt`, containing names of students in `Last Name, First Name` format, like
```
Doe, Jane
Webb, Marvin
Thompson, Emily
```

The script will run if this file does not exist but it won't produce the useful `paried_scores.csv` file.

Now you can run `python main.py /path/to/submissions/directory`. You can also run this directly on a `.zip` file, in
which case it will be extracted to a new directory called `temp_extracted_submissions/`.

## Output

This script will produce a `scores.csv` file and, if you created a `names.txt` file, a `paired_scores.csv` file. The
`scores.csv` contains a list of scores of all the students who submitted, while the `paired_scores.csv` contains a list
of students and the score they received.
The difference is that `paired_scores.csv` will contain entries for students that didn't submit anything, which makes
it easier to paste it into a spreadsheet (since you don't need to match names manually).

You can open the file in LibreOffice Calc or Microsoft Excel, or you can upload it to Google Drive and use Google Sheets
to open the file.
