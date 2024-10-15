from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from styles.models import Style
from geopackages.models import Geopackage
from layerdefinitions.models import LayerDefinition
from wavefronts.models import Wavefront
from models.models import Model



def homepage(request):
    """
    Renders the home page
    """
    latest_styles = Style.objects.filter(approved=True).order_by("-upload_date")[:3]
    latest_geopackages = Geopackage.objects.filter(approved=True).order_by("-upload_date")[:3]
    latest_layerdefinitions = LayerDefinition.objects.filter(approved=True).order_by("-upload_date")[:3]
    latest_wavefronts = Wavefront.objects.filter(approved=True).order_by("-upload_date")[:3]
    latest_models = Model.objects.filter(approved=True).order_by("-upload_date")[:3]

    return render(
        request,
        "flatpages/homepage.html",
        {
            "latest_styles": latest_styles,
            "latest_geopackages": latest_geopackages,
            "latest_layerdefinitions": latest_layerdefinitions,
            "latest_wavefronts": latest_wavefronts,
            "latest_models": latest_models,
            "title": "QGIS resources hub web portal"
        },
    )