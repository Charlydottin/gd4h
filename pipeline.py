#!/usr/bin/.venv/python3.8
#!/usr/bin/.venv/python3.8
import os
import shutil
from scripts.init_db import import_rules, import_references
from scripts.generate_api import generate_app

if __name__ == "__main__":
    import_rules()
    import_references()
    back_app_name = "new_back"
    back_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), back_app_name)
    try:
        shutil.rmtree(back_dir)
    except FileNotFoundError:
        pass
    generate_app(back_app_name)