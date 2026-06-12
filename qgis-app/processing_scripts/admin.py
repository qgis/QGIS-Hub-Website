from django.contrib import admin
from processing_scripts.models import ProcessingScript, PyQtVersion, Review


@admin.register(PyQtVersion)
class PyQtVersionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "description",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("order", "name")


class ProcessingScriptInline(admin.TabularInline):
    model = Review
    list_display = ("review_date", "comment", "reviewer")


@admin.register(ProcessingScript)
class ProcessingScriptAdmin(admin.ModelAdmin):
    inlines = [
        ProcessingScriptInline,
    ]
    list_display = (
        "name",
        "description",
        "creator",
        "upload_date",
        "get_pyqt_versions",
    )
    search_fields = (
        "name",
        "description",
    )
    filter_horizontal = ("pyqt_versions",)

    def get_pyqt_versions(self, obj):
        """Display PyQt versions in list view"""
        return ", ".join([v.name for v in obj.pyqt_versions.all()])

    get_pyqt_versions.short_description = "PyQt Versions"


@admin.register(Review)
class ProcessingScriptReviewAdmin(admin.ModelAdmin):
    list_display = (
        "resource",
        "reviewer",
        "comment",
        "review_date",
    )
