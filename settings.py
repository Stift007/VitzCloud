import os
from dotenv import load_dotenv
from pathlib import Path

DEBUG = os.getenv("DEBUG",False)

if DEBUG:
    end_path = Path(".") / ".env.debug"
    load_dotenv(end_path)
    from settings_files.development import *
    print("EXPORT_MODE: DEBUG")
else:
    print("EXPORT_MODE: PRODUCTION")
    from settings_files.product import *
    