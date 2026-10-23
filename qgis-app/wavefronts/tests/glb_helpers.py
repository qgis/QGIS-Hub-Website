"""Build GLB files for the tests.

A GLB file is a small binary container: a 12 byte header, then one chunk
holding the glTF description as JSON. Building them here lets each test ask
for the broken file it needs, one keyword argument at a time.

These models carry no geometry, because the checks on the way in only read
the description. For a real model with geometry, materials and a texture,
use tree.glb in wavefrontfiles.
"""

import io
import json
import struct
from zipfile import ZipFile

MINIMAL_GLTF = {
    "asset": {"version": "2.0", "generator": "QGIS Hub tests"},
    "scene": 0,
    "scenes": [{"nodes": []}],
    "nodes": [],
}


def make_glb(
    gltf=None,
    magic=b"glTF",
    version=2,
    declared_length=None,
    chunk_type=b"JSON",
) -> bytes:
    """Return the bytes of a GLB file.

    Pass the keyword arguments to break one part of the container and leave
    the rest valid.
    """
    payload = json.dumps(MINIMAL_GLTF if gltf is None else gltf).encode("utf-8")
    # Every chunk is padded to a four byte boundary.
    payload += b" " * ((4 - len(payload) % 4) % 4)

    chunk = struct.pack("<I4s", len(payload), chunk_type) + payload
    length = 12 + len(chunk) if declared_length is None else declared_length
    header = struct.pack("<4sII", magic, version, length)
    return header + chunk


def make_glb_zip(names=("tree.glb",), gltf=None, extra_files=None) -> bytes:
    """Return the bytes of a zip file holding one GLB file, or several."""
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name in names:
            archive.writestr(name, make_glb(gltf=gltf))
        for name, content in (extra_files or {}).items():
            archive.writestr(name, content)
    return buffer.getvalue()
