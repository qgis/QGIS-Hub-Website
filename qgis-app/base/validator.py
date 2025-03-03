import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

RESOURCE_MAX_SIZE = getattr(settings, "RESOURCE_MAX_SIZE", 1000000)  # 1MB
GPKG_MAX_SIZE = getattr(settings, "GPKG_MAX_SIZE", 5000000)  # 5MB
MAP_MAX_SIZE = getattr(settings, "MAP_MAX_UPLOAD_SIZE", 10000000)  # 10 mb


def filesize_validator(file, is_gpkg=False, is_map=False) -> bool:
    """File Size Validation"""
    max_size = GPKG_MAX_SIZE if is_gpkg else RESOURCE_MAX_SIZE
    max_size = MAP_MAX_SIZE if is_map else max_size

    error_filesize_too_big = ValidationError(
        _("File is too big. Max size is %s Megabytes") % (max_size / 1000000)
    )
    try:
        if file.getbuffer().nbytes > max_size:
            raise error_filesize_too_big
    except AttributeError:
        try:
            file.seek(0, os.SEEK_END)
            if file.seek(0, os.SEEK_END) > max_size:
                raise error_filesize_too_big
        except AttributeError:
            try:
                if file.size > max_size:
                    raise error_filesize_too_big
            except AttributeError:
                try:
                    if file.len > max_size:
                        raise error_filesize_too_big
                except Exception:
                    raise error_filesize_too_big
    return True
