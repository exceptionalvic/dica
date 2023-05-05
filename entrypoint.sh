#!/bin/sh

set -e
# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."

#     while ! nc -z $DB_HOST $DB_PORT; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi
python manage.py collectstatic --no-input;
echo "collectstatic ran successfully"
python manage.py migrate --no-input;
echo "migration successful"


exec "$@"