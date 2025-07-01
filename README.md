# Ebook Reader App

This is a simple cross-platform ebook reader built with Python and Tkinter. It supports TXT, PDF, and EPUB files (if the required libraries are installed).

## Features
- Library grid view with book cards
- Pagination (no scrolling) with page-turning
- Font size and style controls
- Chapter-aware pagination (new page at each "chapter ...")
- Add/remove ebooks
- User-friendly error messages

## Requirements
- Python 3.7+
- Tkinter (usually included with Python)
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) (`pip install pymupdf`) for PDF support
- [EbookLib](https://github.com/aerkalov/ebooklib) (`pip install ebooklib`) for EPUB support

## How to Run
1. Install dependencies:
   ```sh
   pip install pymupdf ebooklib
   ```
   (You can skip any you don't need.)
2. Run the app:
   ```sh
   python ebook_reader.py
   ```

## Packaging as an Executable
You can use [PyInstaller](https://pyinstaller.org/) to package the app as a standalone executable:

1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
2. Package the app:
   ```sh
   pyinstaller --onefile --noconsole --add-data "ebooks;ebooks" ebook_reader.py
   ```
   - On Windows, use `;` as the separator in `--add-data`. On Mac/Linux, use `:`.
   - This will create a `dist/ebook_reader.exe` (Windows) or `dist/ebook_reader` (Mac/Linux).
3. Distribute the `dist/` folder. Make sure the `ebooks` folder is included.

## Notes
- The app creates an `ebooks` folder for your library.
- Only supported file types are shown/uploaded.
- If you want to reset your library, just delete the `ebooks` folder.

---

Enjoy reading!
