from base.validator import filesize_validator
from geopackages.models import Geopackage
from models.models import Model
from rest_framework import serializers
from styles.models import Style, StyleType
from layerdefinitions.models import LayerDefinition
from wavefronts.models import WAVEFRONTS_STORAGE_PATH, Wavefront
from map_gallery.models import Map
from screenshots.models import Screenshot
from processing_scripts.models import ProcessingScript
from sorl.thumbnail import get_thumbnail
from django.conf import settings
from os.path import exists, join
from django.templatetags.static import static
from wavefronts.validator import WavefrontValidator

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from styles.file_handler import read_xml_style, validator as style_validator
from layerdefinitions.file_handler import get_provider, get_url_datasource, validator as layer_validator
import tempfile

class ResourceBaseSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="get_creator_name")
    resource_type = serializers.SerializerMethodField()
    resource_subtypes = serializers.SerializerMethodField()
    thumbnail_full = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "resource_type",
            "resource_subtypes",
            "uuid",
            "name",
            "creator",
            "upload_date",
            "download_count",
            "description",
            "file",
            "thumbnail",
            "thumbnail_full"
        ]

    def validate(self, attrs):
        file = attrs.get("file")
        filesize_validator(file)
        return attrs

    def get_resource_type(self, obj):
        if self.Meta.model.__name__ == "Wavefront":
            return "3DModel"
        return self.Meta.model.__name__

    def get_thumbnail_full(self, obj):
        request = self.context.get('request')
        file_field = getattr(obj, "file", None) if self.Meta.model.__name__ in ["Map", "Screenshot"] else getattr(obj, "thumbnail_image", None)

        if file_field and exists(file_field.path):
            if request is not None:
                return request.build_absolute_uri(file_field.url)
            return file_field.url

        return None

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        thumbnail_field = getattr(obj, "thumbnail_image", None)
        try:
            if thumbnail_field and exists(thumbnail_field.path):
                thumbnail = get_thumbnail(thumbnail_field, "128x128", crop="center")
                if request is not None:
                    return request.build_absolute_uri(thumbnail.url)
                return thumbnail.url
        except Exception as e:
            pass

        # Return a full URL to a default image if no thumbnail exists or if there's an error
        default_url = static("theme/images/qgis-icon-32x32.png")
        if request is not None:
            return request.build_absolute_uri(default_url)
        return default_url


class GeopackageSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Geopackage

    def get_resource_subtypes(self, obj):
        return None


class ModelSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Model
        fields = [
             "resource_type",
             "resource_subtypes",
             "uuid",
             "name",
             "creator",
             "upload_date",
             "download_count",
             "description",
             "dependencies",
             "file",
             "thumbnail",
             "thumbnail_full"
         ]

    def get_resource_subtypes(self, obj):
        return None


class StyleSerializer(ResourceBaseSerializer):
    resource_subtypes = serializers.ReadOnlyField(source="get_style_types")

    class Meta(ResourceBaseSerializer.Meta):
        model = Style

    def validate(self, attrs):
        """
        Validate a style file.
        We need to check if the uploaded file is a valid XML file.
        Then, we upload the file to a temporary file, validate it
        and check if the style type is defined.
        """
        attrs = super().validate(attrs)
        file = attrs.get("file")

        if not file:
            raise ValidationError(_("File is required."))

        if file.size == 0:
            raise ValidationError(_("Uploaded file is empty."))
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                with open(temp_file.name, 'rb') as xml_file:
                    style = style_validator(xml_file)
                    xml_parse = read_xml_style(xml_file)
                    style_types_list = xml_parse.get("types", []) if xml_parse else []
                    for type_str in style_types_list:
                        stype = StyleType.objects.filter(symbol_type=type_str).first()
                        if not stype:
                            stype = StyleType.objects.create(
                                symbol_type=type_str,
                                name=type_str.title(),
                                description="Automatically created from an uploaded Style file",
                            )
                        attrs.setdefault("style_types", []).append(stype.id)

                    if not style:
                        raise ValidationError(
                            _("Undefined style type. Please register your style type.")
                        )
        finally:
            import os
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)

        return attrs

class LayerDefinitionSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = LayerDefinition

    def get_resource_subtypes(self, obj):
        return None

    def validate(self, attrs):
        """
        Validate a qlr file.
        We need to check if the uploaded file is a valid QLR file.
        Then, we upload the file to a temporary file and validate it
        """
        attrs = super().validate(attrs)
        file = attrs.get("file")

        if not file:
            raise ValidationError(_("File is required."))

        if file.size == 0:
            raise ValidationError(_("Uploaded file is empty."))
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                with open(temp_file.name, 'rb') as qlr_file:
                    layer_validator(qlr_file)
                    self.url_datasource = get_url_datasource(qlr_file)
                    self.provider = get_provider(qlr_file)


        finally:
            import os
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)

        return attrs

class WavefrontSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Wavefront

    def get_resource_subtypes(self, obj):
        return None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        file = attrs.get("file")
        if file and file.name.endswith('.zip'):
            valid_3dmodel = WavefrontValidator(file).validate_wavefront()
            self.new_filepath = join(WAVEFRONTS_STORAGE_PATH, valid_3dmodel)
        return attrs


class MapSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Map
        fields = [
            "resource_type",
            "resource_subtypes",
            "uuid",
            "id",
            "name",
            "creator",
            "upload_date",
            "download_count",
            "description",
            "file",
            "thumbnail",
            "is_publishable"
        ]

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        thumbnail_field = getattr(obj, "file", None)
        try:
            if thumbnail_field and exists(thumbnail_field.path):
                thumbnail = get_thumbnail(thumbnail_field, "1024x1024", format="WEBP")
                if request is not None:
                    return request.build_absolute_uri(thumbnail.url)
                return thumbnail.url
        except Exception as e:
            pass


    def get_resource_subtypes(self, obj):
        return None


class ScreenshotSerializer(MapSerializer):
    """
    Serializer for Screenshot model, inheriting from MapSerializer
    """
    class Meta(MapSerializer.Meta):
        model = Screenshot
        fields = MapSerializer.Meta.fields

class ProcessingScriptSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = ProcessingScript
        fields = [
            "resource_type",
            "resource_subtypes",
            "uuid",
            "name",
            "creator",
            "upload_date",
            "download_count",
            "description",
            "dependencies",
            "file",
            "thumbnail",
            "thumbnail_full"
        ]

    def get_resource_subtypes(self, obj):
        return None
