"""Wavefront validator."""

import json
import os
import re
import shutil
import struct
import uuid
from zipfile import ZipFile

import pywavefront
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wavefronts.models import WAVEFRONTS_STORAGE_PATH

# A GLB file starts with a 12 byte header: the magic word "glTF", the
# container version and the total length of the file.
GLB_MAGIC = b"glTF"
GLB_HEADER_LENGTH = 12
GLB_CHUNK_HEADER_LENGTH = 8
GLB_JSON_CHUNK_TYPE = b"JSON"

# Extensions a model may not require, because the viewer cannot draw them
# without shipping an extra decoder.
UNSUPPORTED_GLB_EXTENSIONS = (
    "KHR_draco_mesh_compression",
    "KHR_texture_basisu",
    "EXT_meshopt_compression",
)


def read_glb_json(file) -> dict:
    """Read and check the structure of a GLB file.

    Returns the decoded glTF JSON chunk. Raises a ValidationError with a
    message we can show to the uploader when the file is not a GLB we can
    draw.
    """
    file.seek(0)
    content = file.read()
    file.seek(0)

    if len(content) < GLB_HEADER_LENGTH:
        raise ValidationError(_("This file is too short to be a GLB file."))

    magic, version, declared_length = struct.unpack_from("<4sII", content, 0)
    if magic != GLB_MAGIC:
        raise ValidationError(
            _("This is not a GLB file. A GLB file starts with the word glTF.")
        )
    if version != 2:
        raise ValidationError(
            _("We support glTF version 2 only. This file says version %(version)s.")
            % {"version": version}
        )
    if declared_length != len(content):
        raise ValidationError(
            _("This GLB file looks truncated. Export it again and upload the new file.")
        )

    offset = GLB_HEADER_LENGTH
    if len(content) < offset + GLB_CHUNK_HEADER_LENGTH:
        raise ValidationError(_("This GLB file has no model data in it."))

    chunk_length, chunk_type = struct.unpack_from("<I4s", content, offset)
    if chunk_type != GLB_JSON_CHUNK_TYPE:
        raise ValidationError(_("This GLB file has no model description in it."))

    chunk_start = offset + GLB_CHUNK_HEADER_LENGTH
    chunk_end = chunk_start + chunk_length
    if chunk_end > len(content):
        raise ValidationError(
            _("This GLB file looks truncated. Export it again and upload the new file.")
        )

    try:
        gltf = json.loads(content[chunk_start:chunk_end].decode("utf-8"))
    except Exception:
        raise ValidationError(_("We could not read the model description in this GLB file."))

    if not isinstance(gltf, dict):
        raise ValidationError(_("We could not read the model description in this GLB file."))

    asset_version = str(gltf.get("asset", {}).get("version", ""))
    if not asset_version.startswith("2."):
        raise ValidationError(
            _("We support glTF version 2 only. This file says version %(version)s.")
            % {"version": asset_version or _("unknown")}
        )

    for extension in gltf.get("extensionsRequired", []):
        if extension in UNSUPPORTED_GLB_EXTENSIONS:
            raise ValidationError(
                _(
                    "This model needs the %(extension)s extension, which our viewer "
                    "cannot draw. Export it again without compression."
                )
                % {"extension": extension}
            )

    for key in ("buffers", "images"):
        for entry in gltf.get(key, []):
            uri = entry.get("uri") if isinstance(entry, dict) else None
            if uri and not uri.startswith("data:"):
                raise ValidationError(
                    _(
                        "This GLB file points at the separate file %(uri)s. Export it "
                        "again with the textures and the mesh inside the GLB file."
                    )
                    % {"uri": uri}
                )

    return gltf


class WavefrontValidator:
    def __init__(self, file):
        self.file = file

    def validate(self):
        """Validate an uploaded 3D model.

        Accepts a GLB file, a zip file holding one GLB file, or a zip file
        holding an OBJ file and its MTL file.

        Returns the path to store in the file field, relative to the
        wavefronts media folder, or None to store the upload as it arrives.
        """
        name, ext = os.path.splitext(getattr(self.file, "name", "") or "")
        if ext.lower() == ".glb":
            return self.validate_glb()
        if self.get_glb_paths():
            return self.validate_zipped_glb()
        return self.validate_wavefront()

    def valid_zip(self):
        try:
            zip_file = ZipFile(self.file)
        except Exception:
            raise ValidationError(_("Could not unzip file."))
        return zip_file

    def get_glb_paths(self):
        """Return the paths of every GLB file in the archive."""
        rgx = r".*\.glb$"
        return [
            file.filename
            for file in self.valid_zip().filelist
            if not file.filename.endswith("/") and re.findall(rgx, file.filename)
        ]

    def get_wavefront_obj_path(self):
        rgx = r".*\.obj$"
        for file in self.valid_zip().filelist:
            find_wavefront = re.findall(rgx, file.filename)
            if find_wavefront and find_wavefront[0]:
                # get the path of .obj file
                return find_wavefront[0]
        raise ValidationError(_("Could not find .obj file."))

    def is_mtl_file_exist(self):
        obj_path = self.get_wavefront_obj_path()
        filename, ext = os.path.splitext(obj_path)
        mtl_file = f"{filename}.mtl"
        for file in self.valid_zip().filelist:
            if mtl_file == file.filename:
                return True
        raise ValidationError(_("Could not find .mtl file."))

    def extract_zipfile(self, target_dir):
        with ZipFile(self.file) as zip:
            for zip_info in zip.infolist():
                if zip_info.filename[-1] == "/":
                    continue
                zip_info.filename = os.path.basename(zip_info.filename)
                zip.extract(zip_info, target_dir)

    def validate_glb(self):
        """Validate a GLB file uploaded on its own.

        A GLB file carries the mesh, the materials and the textures, so there
        is nothing to unpack. We return None and let the file field store the
        upload where it normally would.
        """
        read_glb_json(self.file)
        return None

    def validate_zipped_glb(self):
        """Validate a zip file holding one GLB file.

        The archive is unpacked into its own folder so any read me or licence
        file next to the model is kept. The returned path names a zip file in
        that folder, which is where the file field stores the upload.
        """
        glb_paths = self.get_glb_paths()
        if len(glb_paths) > 1:
            raise ValidationError(
                _(
                    "This zip file holds %(count)s GLB files. Upload one model at a "
                    "time so we know which one to show."
                )
                % {"count": len(glb_paths)}
            )

        glb_path = glb_paths[0]
        filename, ext = os.path.splitext(os.path.basename(glb_path))

        unique_hex = uuid.uuid4().hex[0:6]
        temp_dir = f"/tmp/{unique_hex}"
        os.makedirs(temp_dir, exist_ok=True)
        temp_glb = os.path.join(temp_dir, f"{filename}.glb")
        try:
            with open(temp_glb, "wb") as f_glb:
                f_glb.write(self.valid_zip().read(glb_path))
            with open(temp_glb, "rb") as f_glb:
                read_glb_json(f_glb)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # save to media directory
        media_dir = os.path.join(settings.MEDIA_ROOT, WAVEFRONTS_STORAGE_PATH)
        save_dir = os.path.join(media_dir, unique_hex)
        os.makedirs(save_dir, exist_ok=True)
        self.extract_zipfile(save_dir)

        return f"{unique_hex}/{filename}.zip"

    def validate_wavefront(self):
        self.is_mtl_file_exist()
        obj_path = self.get_wavefront_obj_path()
        filename, ext = os.path.splitext(obj_path)
        mtl_path = f"{filename}.mtl"

        unique_hex = uuid.uuid4().hex[0:6]
        temp_dir = f"/tmp/{unique_hex}"

        # create new directory for temporary file
        path, filename = os.path.split(obj_path)
        filename, ext = os.path.splitext(filename)
        obj_file = f"{filename}.obj"
        mtl_file = f"{filename}.mtl"
        dummy_file = f"{filename}.zip"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        with open(f"{temp_dir}/{obj_file}", "wb") as f_obj:
            f_obj.write(ZipFile(self.file).read(obj_path))
        with open(f"{temp_dir}/{mtl_file}", "wb") as f_mtl:
            f_mtl.write(ZipFile(self.file).read(mtl_path))

        try:
            pywavefront.Wavefront(f"{temp_dir}/{obj_file}")
        except Exception as e:
            raise ValidationError(_(f"Wavefront validation failed. {e}"))

        # save to media directory
        media_dir = os.path.join(settings.MEDIA_ROOT, WAVEFRONTS_STORAGE_PATH)
        save_dir = f"{media_dir}/{unique_hex}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.extract_zipfile(save_dir)

        # remove temp directory and the content
        shutil.rmtree(temp_dir)

        return f"{unique_hex}/{dummy_file}"
