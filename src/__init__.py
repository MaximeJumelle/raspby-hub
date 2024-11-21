import os
import sys
import re

from typing import Dict, Any


conf: Dict[str, Any] = {}

# Loading config file
if not os.path.exists("./properties.conf"):
    raise SystemExit("Fatal: Missing 'properties.conf' file.")

with open("./properties.conf") as f:
    for line in f:
        if re.match(r"^.*\s*=\s*(\".*\"|\d*\.?\d*)$", line):
            line = line.replace("\n", "")
            key = line.split("=")[0].replace(" ", "")
            value = "=".join(line.split("=")[1:])
            value = re.sub(r"^\s*|\s*$", "", value)

            # First of all, if the environment variable is already defined, we take it as a reference
            if key in os.environ:
               continue
            # Here, we should allow some environment variable to override some properties

            # Environment variables have priority over the server.properties file
            if key.replace(".", "_").upper() in os.environ:
                if os.environ[key] in ["true", "false"]:
                    conf[key] = value == "true"
                else:
                    conf[key] = os.environ[key]
            # If quotes, consider it as a string
            elif value[0] == '"':
                conf[key] = str(value.replace('"', ""))
            elif value in ["true", "false"]:
                conf[key] = value == "true"
            else:  # We store it as a string
                conf[key] = str(value)

if getattr(sys, "frozen", False):
    # When compiled, PyInstaller create an MEI folder in /tmp/..., so that all data files are located here
    os.chdir(sys._MEIPASS)  # type: ignore