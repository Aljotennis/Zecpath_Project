
import os
import zipfile

from django.core.exceptions import ValidationError


MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_resume_file(file):
    # 1. Check file size
    if file.size > MAX_RESUME_SIZE:
        raise ValidationError("Resume file must not exceed 5 MB.")

    # 2. Check file extension
    extension = os.path.splitext(file.name)[1].lower()

    allowed_extensions = [".pdf", ".doc", ".docx"]

    if extension not in allowed_extensions:
        raise ValidationError(
            "Only PDF, DOC and DOCX files are allowed."
        )

    # 3. Read file content for validation
    file.seek(0)
    file_header = file.read(8)
    file.seek(0)

    # 4. Validate actual file format
    if extension == ".pdf":
        if not file_header.startswith(b"%PDF-"):
            raise ValidationError("Invalid PDF file.")

    elif extension == ".doc":
        if file_header != bytes.fromhex("D0CF11E0A1B11AE1"):
            raise ValidationError("Invalid DOC file.")

    elif extension == ".docx":
        try:
            with zipfile.ZipFile(file) as archive:
                files = archive.namelist()

                if (
                    "[Content_Types].xml" not in files
                    or "word/document.xml" not in files
                ):
                    raise ValidationError("Invalid DOCX file.")

        except (zipfile.BadZipFile, OSError):
            raise ValidationError("Invalid DOCX file.")

        finally:
            file.seek(0)
