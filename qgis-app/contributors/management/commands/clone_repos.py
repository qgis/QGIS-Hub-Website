import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

REPOS = [
    "QGIS-Website",
    "QGIS-Plugins-Website",
    "QGIS-Hub-Website",
    "QGIS-Planet-Website",
    "QGIS-Certification-Website",
    "QGIS-Changelog-Website",
    "QGIS-Members-Website",
    "QGIS-UC-Website",
    "QGIS-Feed-Website",
    "QGIS-Documentation",
    "QGIS",
]


class Command(BaseCommand):
    help = "Clone QGIS repositories from GitHub using --bare option"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dest",
            type=str,
            default=os.path.join(settings.SITE_ROOT, "qgis_repos"),
            help="Destination directory for bare repositories",
        )

    def _fix_bare_repo_config(self, repo_path):
        subprocess.run(
            [
                "git",
                "config",
                "remote.origin.fetch",
                "+refs/heads/*:refs/remotes/origin/*",
            ],
            cwd=repo_path,
            check=True,
        )
        subprocess.run(
            ["git", "remote", "set-head", "origin", "-a"], cwd=repo_path, check=True
        )

    def handle(self, *args, **options):
        dest_dir = options["dest"]
        os.makedirs(dest_dir, exist_ok=True)

        for repo_name in REPOS:
            repo_url = f"https://github.com/qgis/{repo_name}.git"
            repo_path = os.path.join(dest_dir, repo_name)
            if os.path.exists(repo_path):
                self.stdout.write(
                    self.style.WARNING(f"{repo_name} already exists, skipping.")
                )
                self._fix_bare_repo_config(repo_path)
                continue
            self.stdout.write(f"Cloning {repo_url} into {repo_path} ...")
            try:
                subprocess.check_call(["git", "clone", "--bare", repo_url, repo_path])
                self._fix_bare_repo_config(repo_path)
                self.stdout.write(
                    self.style.SUCCESS(f"Cloned {repo_name} successfully.")
                )
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(f"Failed to clone {repo_url}: {e}"))
