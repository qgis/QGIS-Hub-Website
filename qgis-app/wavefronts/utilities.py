import io
import os.path
from zipfile import ZIP_DEFLATED, ZipFile

from base.license import LICENSE_FILE


def get_viewer_context(wavefront) -> dict:
    """Return what the 3D viewer needs to load a model.

    A GLB carries its own materials, so it loads from one url. An obj model
    loads its mtl file alongside, under the same name.
    """
    stem, extension = os.path.splitext(wavefront.file.url)
    model_format = wavefront.model_format
    context = {"model_format": model_format}
    if model_format == "glb":
        context["model_url"] = f"{stem}.glb"
    else:
        context["model_url"] = f"{stem}.obj"
        context["obj_url"] = f"{stem}.obj"
        context["mtl_url"] = f"{stem}.mtl"
    return context


def zipped_all_with_license(folder_path: str, zip_subdir: str) -> io.BytesIO:
    """Zip all wavefront files with license."""
    if not os.path.isdir(folder_path):
        return None

    in_memory_data = io.BytesIO()
    filelist = os.listdir(folder_path)
    filelist.append(LICENSE_FILE)
    with ZipFile(in_memory_data, "w", ZIP_DEFLATED) as zf:
        for file in filelist:
            if file.endswith(".zip"):
                continue
            file_path, filename = os.path.split(file)
            zf.write(
                os.path.join(folder_path, file), os.path.join(zip_subdir, filename)
            )
    return in_memory_data
