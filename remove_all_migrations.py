import os
import shutil

# Set the DJANGO_SETTINGS_MODULE environment variable to point to your project's settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Universal_HRMS.settings")

# Get the list of installed apps from your project's settings.
from django.conf import settings
installed_apps = settings.INSTALLED_APPS

# Define the path to the root directory of your project.
project_root = os.getcwd()

# Function to remove __pycache__ folders and migration files for a specific app.
def remove_app_files(app_name):
    # Remove __pycache__ folders within the app directory.
    app_dir = os.path.join(project_root, app_name)
    for dirpath, dirnames, filenames in os.walk(app_dir):
        for dirname in dirnames:
            if dirname == '__pycache__':
                pycache_dir = os.path.join(dirpath, dirname)
                shutil.rmtree(pycache_dir)
                print(f"Removed __pycache__ folder in app: {app_name}")

    # Remove migration files and their __pycache__ folders.
    migrations_dir = os.path.join(project_root, app_name, 'migrations')
    if os.path.exists(migrations_dir):
        migration_files = os.listdir(migrations_dir)
        for file in migration_files:
            if file.endswith('.py') and file != '__init__.py':
                migration_file_path = os.path.join(migrations_dir, file)
                os.remove(migration_file_path)
                print(f"Deleted migration file: {file}")

                # Remove __pycache__ for migration file, if it exists.
                pycache_migration_file = f"{file}c"
                pycache_migration_file_path = os.path.join(migrations_dir, pycache_migration_file)
                if os.path.exists(pycache_migration_file_path):
                    os.remove(pycache_migration_file_path)
                    print(f"Deleted __pycache__ for migration file: {pycache_migration_file}")

# Iterate through all installed apps and remove their __pycache__ folders and migration files.
for app_name in installed_apps:
    remove_app_files(app_name)

print("Removed all __pycache__ folders and migration files (except __init__.py) from all apps.")
