# import os
# from django.core.management import execute_from_command_line

# if __name__ == "__main__":
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appraisal_project.settings")
#     execute_from_command_line(["manage.py", "runserver", "127.0.0.1:5000"])

import os
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appraisal_project.settings")
    port = int(os.getenv('PORT', 5000))
    execute_from_command_line(["manage.py", "runserver", f"0.0.0.0:{port}"])
