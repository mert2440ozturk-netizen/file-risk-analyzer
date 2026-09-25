# File Risk Analyzer

A desktop tool that performs basic, rule-based risk checks on a single file.
It inspects the file name and the file's actual content signature (magic bytes)
to spot common tricks such as misleading double extensions.

> **Note:** This is a learning project, not an antivirus. A low score does not
> mean a file is safe. The tool never executes the files it analyzes.
> 

## Features

- Drag-and-drop or file-picker selection (PySide6 GUI)
- Analysis runs in a background thread, so the interface stays responsive
- File signature detection: PDF, PNG, ZIP-based containers, empty files
- SHA-256 hash calculation (read in 1 MiB chunks to limit memory use)
- Rule-based findings with severity levels and a 1–5 risk score

## Current rules

| Rule | Severity | Example |
|------|----------|---------|
| Misleading double extension | medium | `invoice.pdf.exe` |
| Extension does not match content signature | low | a PNG file named `photo.pdf` |

The risk score is the highest severity among all findings.
If the file type cannot be identified and no rule matched, the file is
marked as **"Not scored"** instead of receiving a misleadingly low score.

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/mert2440ozturk-netizen/file-risk-analyzer.git
cd file-risk-analyzer
python -m venv .venv
```

Activate the virtual environment:

- Windows: `.venv\Scripts\activate`
- macOS / Linux: `source .venv/bin/activate`

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Graphical interface:

```bash
python main.py
```

Command-line version:

```bash
python analyzer.py
```

## Running the tests

```bash
python -m pytest -v
```

## Limitations

- Only a small set of file signatures is recognized.
- ZIP-based files (DOCX, XLSX, JAR, etc.) are not inspected internally yet.
- Executables disguised with a document extension are not detected yet
  (tracked by an expected-failure test).

## Roadmap

- [ ] Executable signature detection (PE / ELF)
- [ ] File name tricks (RTLO character, padded spaces, risky extensions)
- [ ] ZIP / Office / PDF content inspection
- [ ] Entropy analysis
- [ ] Hash lookup via threat intelligence services
- [ ] Report export (JSON / HTML)