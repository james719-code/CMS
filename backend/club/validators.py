from pathlib import Path

from rest_framework import serializers


IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "jpeg", "png"}
RECEIPT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

MAX_IMAGE_SIZE = 2 * 1024 * 1024
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
MAX_RECEIPT_SIZE = 5 * 1024 * 1024


def validate_upload(file_obj, allowed_extensions, max_size, label):
    if not file_obj:
        return file_obj

    extension = Path(file_obj.name).suffix.lower().lstrip(".")
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise serializers.ValidationError(f"{label} must use one of these file types: {allowed}.")

    if file_obj.size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise serializers.ValidationError(f"{label} must be {max_mb}MB or smaller.")

    return file_obj


def validate_image_file(file_obj):
    return validate_upload(file_obj, IMAGE_EXTENSIONS, MAX_IMAGE_SIZE, "Image")


def validate_document_file(file_obj):
    return validate_upload(file_obj, DOCUMENT_EXTENSIONS, MAX_DOCUMENT_SIZE, "Document")


def validate_receipt_file(file_obj):
    return validate_upload(file_obj, RECEIPT_EXTENSIONS, MAX_RECEIPT_SIZE, "Receipt")
