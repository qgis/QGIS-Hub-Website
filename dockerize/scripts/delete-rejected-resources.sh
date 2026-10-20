#!/usr/bin/env bash


# Remove rejected resources that the author never fixed.
#
# A reviewer who rejects a resource gives the author a grace period to fix it,
# set by REJECTED_RESOURCE_GRACE_DAYS and 7 days by default. This script removes
# anything still waiting for a fix after that.
#
# Run daily on crontab e.g.
#  Your cron job will be run at: (5 times displayed)
#
#    2026-11-08 03:30:00 UTC
#    2026-11-09 03:30:00 UTC
#    2026-11-10 03:30:00 UTC
#    2026-11-11 03:30:00 UTC
#    2026-11-12 03:30:00 UTC
#    ...etc

#30 3 * * * /bin/bash /home/QGIS-Hub-Website/dockerize/scripts/delete-rejected-resources.sh > /tmp/delete-rejected-resources-logs.txt

# Drop the --commit flag below to see what would be removed without removing it.

# Set common variables
COMPOSE_FILE="/home/QGIS-Hub-Website/dockerize/docker-compose.yml"
PROJECT_NAME="qgis-hub"

# Remove the abandoned resources
docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" run --rm uwsgi \
    python manage.py delete_rejected_resources --commit
