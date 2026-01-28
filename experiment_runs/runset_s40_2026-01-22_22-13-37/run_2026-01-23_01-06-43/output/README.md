# File Organizer CLI Tool

A collaborative project by Alice and Bob - a practical command-line utility for organizing messy directories.

## Features

- **Organize by file type**: Automatically categorizes files into folders like `images/`, `documents/`, `code/`, etc.
- **Dry run mode**: Preview what will be organized before making changes
- **Comprehensive file type support**: Handles images, documents, spreadsheets, videos, audio, archives, and code files
- **Safe operations**: Creates organized folders without overwriting existing files
- **Detailed reporting**: Shows exactly what was moved and provides summary statistics

## Usage

```bash
# Show help
python file_organizer.py -h

# Organize files with preview (recommended first step)
python file_organizer.py organize /path/to/messy/folder --dry-run

# Actually organize the files
python file_organizer.py organize /path/to/messy/folder

# Organize to a custom target directory
python file_organizer.py organize ~/Downloads --target ~/OrganizedFiles
```

## Example Output

```
Organizing files from: test_files
Target directory: test_files/organized_by_type
DRY RUN - No files will be moved
--------------------------------------------------
[DRY RUN] Would move script.py → code/
[DRY RUN] Would move data.csv → spreadsheets/
[DRY RUN] Would move sample.txt → documents/
[DRY RUN] Would move photo.jpg → images/

==================================================
ORGANIZATION SUMMARY
==================================================
Code: 1 files
Spreadsheets: 1 files
Documents: 1 files
Images: 1 files

Total files processed: 4
```

## File Categories

- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`
- **Spreadsheets**: `.xls`, `.xlsx`, `.csv`, `.ods`
- **Presentations**: `.ppt`, `.pptx`, `.odp`
- **Videos**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`
- **Audio**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`
- **Archives**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`
- **Code**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`, `.c`, `.php`, `.rb`
- **Misc**: Everything else

## Next Steps & Ideas for Extension

This tool is designed to be easily extensible. Here are some ideas for future enhancements:

1. **Organize by date**: Group files by creation/modification date
2. **Custom rules**: User-defined organization patterns
3. **Undo functionality**: Ability to reverse organization operations
4. **Duplicate detection**: Find and handle duplicate files
5. **Size-based organization**: Group by file size ranges
6. **Interactive mode**: Ask user for confirmation on ambiguous files
7. **Configuration file**: Save user preferences and custom categories

## Testing

The project includes a `test_files/` directory with sample files for testing the organizer safely.