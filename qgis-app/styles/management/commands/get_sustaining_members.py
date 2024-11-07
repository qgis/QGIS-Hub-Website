from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Get the Sustaining members HTML section from the new website"
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            url = 'https://qgis.org'
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the section by the specified class name
            section = soup.select_one('section.section')

            if section:
                template_path = os.path.join(settings.SITE_ROOT, 'templates/flatpages/sustaining_members.html')
                with open(template_path, 'w') as f:
                    f.write(section.prettify())
                print(f"get_sustaining_members: Section saved to {template_path}")
            else:
                print("get_sustaining_members: Section not found")
        except requests.RequestException as e:
            print(f"get_sustaining_members: {e}")