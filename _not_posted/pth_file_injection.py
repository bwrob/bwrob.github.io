import os
import site


def make_setup_permanent():
    """Finds usercustomize.py and injects auto-imports permanently."""
    # 1. Find the user's specific site-packages directory
    user_site_dir = site.getusersitepackages()

    # 2. Make sure the directory actually exists
    if not os.path.exists(user_site_dir):
        os.makedirs(user_site_dir)

    # 3. Define the path to usercustomize.py
    customize_file = os.path.join(user_site_dir, "usercustomize.py")

    # 4. The exact code you want to inject
    # (We wrap it in a try/except so if they uninstall your package later,
    # their Python doesn't completely break on startup!)
    injection_code = """
# --- Added by My Framework ---
try:
    import builtins
    import math
    import os

    builtins.math = math
    builtins.os = os
except ImportError:
    pass
# -----------------------------
"""

    # 5. Check if we already injected it (to avoid duplicating code)
    if os.path.exists(customize_file):
        with open(customize_file) as file:
            content = file.read()
            if "# --- Added by My Framework ---" in content:
                print("Environment is already permanently set up!")
                return

    # 6. Append our code to the file safely
    with open(customize_file, "a") as file:
        file.write("\n" + injection_code)

    print(f"Success! usercustomize.py has been updated at: {customize_file}")
