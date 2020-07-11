#!/bin/bash
# Make migrations if model changed
./manage.py makemigrations

# Migrate after make migration to create tables
./manage.py migrate

# Create categories from breadcrumbs
./manage.py oscar_create_categories

# Load data from fixture
./manage.py loaddata quiz_maker/fixtures/questions.json

# Load default template
./manage.py loaddata quiz_maker/fixtures/templates.json
