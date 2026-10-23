import io
import os
import tempfile
from unittest import mock
from zipfile import ZipFile

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from wavefronts.models import WAVEFRONTS_STORAGE_PATH
from wavefronts.tests.glb_helpers import MINIMAL_GLTF, make_glb, make_glb_zip
from wavefronts.validator import WavefrontValidator, read_glb_json

WAVEFRONT_DIR = os.path.join(os.path.dirname(__file__), "wavefrontfiles")


class TestWavefrontValidator(TestCase):
    def setUp(self) -> None:
        self.mocked_obj = mock.Mock()
        self.mocked_obj.filename = "root_dir/test.obj"
        self.mocked_mtl = mock.Mock()
        self.mocked_mtl.filename = "root_dir/test.mtl"
        self.mocked_mtl_random = mock.Mock()
        self.mocked_mtl_random.filename = "root_dir/random.mtl"

    def test_get_wavefront_obj_path_succeed(self):
        with mock.patch("wavefronts.validator.WavefrontValidator.valid_zip") as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_obj, self.mocked_mtl]
            wv = WavefrontValidator("test.zip")
            self.assertEqual(wv.get_wavefront_obj_path(), "root_dir/test.obj")

    def test_get_wavefront_obj_path_cannot_find_obj_file(self):
        with mock.patch("wavefronts.validator.WavefrontValidator.valid_zip") as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_mtl]
            wv = WavefrontValidator("test.zip")
            with self.assertRaises(ValidationError) as error:
                wv.get_wavefront_obj_path()
            self.assertEqual(str(error.exception.message), "Could not find .obj file.")

    def test_is_mtl_file_exist_succeed(self):
        with mock.patch("wavefronts.validator.WavefrontValidator.valid_zip") as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_obj, self.mocked_mtl]
            wv = WavefrontValidator("test.zip")
            self.assertTrue(wv.is_mtl_file_exist())

    def test_is_mtl_file_exist_cannot_find_mtl(self):
        with mock.patch("wavefronts.validator.WavefrontValidator.valid_zip") as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_obj, self.mocked_mtl_random]
            wv = WavefrontValidator("test.zip")
            with self.assertRaises(ValidationError) as error:
                wv.is_mtl_file_exist()
            self.assertEqual(str(error.exception.message), "Could not find .mtl file.")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_validate_wavefront(self):
        valid_wavefront = os.path.join(WAVEFRONT_DIR, "odm_texturing_25d.zip")
        wv = WavefrontValidator(valid_wavefront)
        self.assertTrue(wv.validate_wavefront())

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_validate_routes_a_zipped_obj_to_the_wavefront_check(self):
        valid_wavefront = os.path.join(WAVEFRONT_DIR, "odm_texturing_25d.zip")
        wv = WavefrontValidator(valid_wavefront)
        self.assertTrue(wv.validate().endswith("odm_textured_model_geo.zip"))


class TestGlbReader(TestCase):
    """The GLB container check."""

    def read(self, content):
        return read_glb_json(io.BytesIO(content))

    def test_minimal_glb_is_valid(self):
        self.assertEqual(self.read(make_glb())["asset"]["version"], "2.0")

    def test_empty_file(self):
        with self.assertRaises(ValidationError) as error:
            self.read(b"")
        self.assertEqual(
            str(error.exception.message), "This file is too short to be a GLB file."
        )

    def test_wrong_magic_word(self):
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(magic=b"GLTF"))
        self.assertEqual(
            str(error.exception.message),
            "This is not a GLB file. A GLB file starts with the word glTF.",
        )

    def test_container_version_one(self):
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(version=1))
        self.assertIn("version 2 only", str(error.exception.message))

    def test_declared_length_does_not_match(self):
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(declared_length=999999))
        self.assertIn("truncated", str(error.exception.message))

    def test_first_chunk_is_not_the_description(self):
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(chunk_type=b"BIN\x00"))
        self.assertEqual(
            str(error.exception.message),
            "This GLB file has no model description in it.",
        )

    def test_asset_version_one(self):
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(gltf={"asset": {"version": "1.0"}}))
        self.assertIn("version 2 only", str(error.exception.message))

    def test_buffer_pointing_at_a_separate_file(self):
        gltf = dict(MINIMAL_GLTF, buffers=[{"uri": "tree.bin", "byteLength": 4}])
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(gltf=gltf))
        self.assertIn("tree.bin", str(error.exception.message))

    def test_image_pointing_at_a_separate_file(self):
        gltf = dict(MINIMAL_GLTF, images=[{"uri": "https://example.org/bark.png"}])
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(gltf=gltf))
        self.assertIn("bark.png", str(error.exception.message))

    def test_embedded_buffer_is_allowed(self):
        gltf = dict(
            MINIMAL_GLTF,
            buffers=[{"uri": "data:application/octet-stream;base64,AAAA", "byteLength": 3}],
        )
        self.assertTrue(self.read(make_glb(gltf=gltf)))

    def test_compressed_model_is_refused(self):
        gltf = dict(MINIMAL_GLTF, extensionsRequired=["KHR_draco_mesh_compression"])
        with self.assertRaises(ValidationError) as error:
            self.read(make_glb(gltf=gltf))
        self.assertIn("KHR_draco_mesh_compression", str(error.exception.message))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestGlbValidator(TestCase):
    """Uploading a GLB file, on its own or inside a zip file."""

    def fixture(self, name):
        with open(os.path.join(WAVEFRONT_DIR, name), "rb") as model:
            return model.read()

    def test_the_committed_model_is_accepted(self):
        # A real model with geometry, two materials and an embedded texture.
        gltf = read_glb_json(io.BytesIO(self.fixture("tree.glb")))
        self.assertEqual(len(gltf["materials"]), 2)
        self.assertEqual(len(gltf["images"]), 1)
        upload = SimpleUploadedFile("tree.glb", self.fixture("tree.glb"))
        self.assertIsNone(WavefrontValidator(upload).validate())

    def test_the_committed_zip_holds_a_model_we_accept(self):
        upload = SimpleUploadedFile("tree-zipped.zip", self.fixture("tree-zipped.zip"))
        file_path = WavefrontValidator(upload).validate()
        self.assertTrue(file_path.endswith("tree.zip"))
        self.assertEqual(
            sorted(os.listdir(self.stored_folder(file_path))),
            ["readme.txt", "tree.glb"],
        )

    def test_the_committed_broken_model_is_refused(self):
        upload = SimpleUploadedFile(
            "broken-tree.glb", self.fixture("broken-tree.glb")
        )
        with self.assertRaises(ValidationError) as error:
            WavefrontValidator(upload).validate()
        self.assertEqual(
            str(error.exception.message),
            "This is not a GLB file. A GLB file starts with the word glTF.",
        )

    def test_glb_on_its_own_is_stored_as_it_arrives(self):
        upload = SimpleUploadedFile("tree.glb", make_glb())
        self.assertIsNone(WavefrontValidator(upload).validate())

    def test_broken_glb_on_its_own(self):
        upload = SimpleUploadedFile("tree.glb", make_glb(magic=b"GLTF"))
        with self.assertRaises(ValidationError):
            WavefrontValidator(upload).validate()

    def stored_folder(self, file_path):
        return os.path.join(
            settings.MEDIA_ROOT, WAVEFRONTS_STORAGE_PATH, os.path.dirname(file_path)
        )

    def test_zipped_glb_is_unpacked(self):
        upload = SimpleUploadedFile("tree.zip", make_glb_zip(names=["mesh/tree.glb"]))
        file_path = WavefrontValidator(upload).validate()
        # The file field stores a zip file next to the model it holds, so the
        # viewer can find the model under the same name.
        self.assertTrue(file_path.endswith("tree.zip"))
        self.assertEqual(os.listdir(self.stored_folder(file_path)), ["tree.glb"])

    def test_zipped_glb_keeps_the_files_next_to_it(self):
        upload = SimpleUploadedFile(
            "tree.zip",
            make_glb_zip(names=["tree.glb"], extra_files={"readme.txt": "Hello"}),
        )
        file_path = WavefrontValidator(upload).validate()
        self.assertEqual(
            sorted(os.listdir(self.stored_folder(file_path))),
            ["readme.txt", "tree.glb"],
        )

    def test_zip_holding_two_models(self):
        upload = SimpleUploadedFile(
            "trees.zip", make_glb_zip(names=["one.glb", "two.glb"])
        )
        with self.assertRaises(ValidationError) as error:
            WavefrontValidator(upload).validate()
        self.assertIn("2 GLB files", str(error.exception.message))

    def test_broken_glb_inside_a_zip(self):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("tree.glb", b"not a model at all")
        upload = SimpleUploadedFile("tree.zip", buffer.getvalue())
        with self.assertRaises(ValidationError):
            WavefrontValidator(upload).validate()
