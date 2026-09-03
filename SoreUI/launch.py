import sys
import os
import json
import hashlib
from pathlib import Path

_SOREUI_DIR = Path(__file__).parent
_FILES_DIR = _SOREUI_DIR.joinpath("files")
_SETTINGS_PATH = _FILES_DIR.joinpath("settings.json")


def _load_config():
    if not _SETTINGS_PATH.exists():
        print(f"Error: settings.json not found at {_SETTINGS_PATH}")
        sys.exit(1)
    with open(_SETTINGS_PATH, "r") as f:
        return json.load(f)


def _msgbox_win32(typ, title, msg):
    import win32api
    return win32api.MessageBox(0, msg, title, typ)


def _msgbox_console(typ, title, msg):
    prefix = {"Error": "[ERROR]", "Warning": "[WARN]", "Info": "[INFO]"}.get(title, "[MSG]")
    print(f"{prefix} {msg}")
    return 0


def _get_input_console(prompt="Enter text:"):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None


def _get_input_tkinter(title="Input Box", prompt="Enter text:"):
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    result = simpledialog.askstring(title, prompt)
    root.destroy()
    return result


def _get_input(title="Input Box", prompt="Enter text:"):
    if sys.platform == "win32":
        try:
            return _get_input_tkinter(title, prompt)
        except Exception:
            return _get_input_console(prompt)
    return _get_input_console(prompt)


def _msgbox(typ, title, msg):
    if sys.platform == "win32":
        try:
            return _msgbox_win32(typ, title, msg)
        except Exception:
            return _msgbox_console(typ, title, msg)
    return _msgbox_console(typ, title, msg)


def _check_dependencies():
    missing = []
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    try:
        import pyaudio
    except ImportError:
        missing.append("pyaudio")
    if missing:
        print(f"Warning: Missing optional packages: {', '.join(missing)}")
        print("Install them with: pip install " + " ".join(missing))
        print("Continuing anyway...\n")


def main():
    config = _load_config()

    security = config.get("Security", {})
    if security.get("Enabled") and security.get("SecurityMethod") == "Password":
        stored_hash = security.get("SecurityVariables", {}).get("InsecurePassword", "")
        if stored_hash:
            stored_hash = hashlib.sha256(stored_hash.encode()).hexdigest()
            user_input = _get_input("Security", "Enter your password: ")
            if not user_input:
                _msgbox(16, "Error", "Access Denied.\nPlease try again.")
                sys.exit(1)
            if hashlib.sha256(user_input.encode()).hexdigest() != stored_hash:
                _msgbox(16, "Error", "Access Denied.\nPlease try again.")
                sys.exit(1)
            _msgbox(64, "Info", "Access Granted.")

    _check_dependencies()

    sys.path.insert(0, str(_FILES_DIR))

    try:
        import main as main_module
    except ImportError as e:
        print(f"Error importing main module: {e}")
        print("Make sure all dependencies are installed.")
        sys.exit(1)

    main_module.main()


if __name__ == "__main__":
    main()
