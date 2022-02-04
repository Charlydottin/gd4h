#!/usr/bin/.venv/python3.8
#!/usr/bin/.venv/python3.8
import os
import shutil
from scripts.init_db import import_rules, import_references
from scripts.generate_api import generate_app
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("app_name")

if __name__ == "__main__":
    args = parser.parse_args()
    app_name = args.app_name
    print(f"Creating {app_name}")
    print("Initialize DB")
    import_rules()
    import_references()
    print(f"Generate new app into {app_name}")
    # # back_app_name = "new_back"
    back_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), app_name)
    try:
        shutil.rmtree(back_dir)
    except FileNotFoundError:
        pass
    generate_app(app_name)