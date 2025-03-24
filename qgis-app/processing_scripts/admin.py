from django.contrib import admin
from processing_scripts.models import ProcessingScript, Review


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
    )
    search_fields = (
        "name",
        "description",
    )


@admin.register(Review)
class ProcessingScriptReviewAdmin(admin.ModelAdmin):
    list_display = (
        "resource",
        "reviewer",
        "comment",
        "review_date",
    )
