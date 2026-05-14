from __future__ import annotations

import argparse
import os
from pathlib import Path

from .llm import LLMError, get_provider
from .pipeline import load_persona, load_targets, recommend_accounts
from .reporting import write_outputs
from .sheets import SheetsSyncError, sync_to_google_sheets
from .utils import utc_run_id

from .streamlit_app import run_streamlit_app  # NEW IMPORT




# ... (existing content remains unchanged until the argparse section)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gtm-command-center",
        description="Run AI-native GTM account research, scoring, and draft generation.",
    )
    parser.add_argument(
        "run",
        nargs="?",
        default="run",
        help="Command to run. Currently only 'run' is supported."
    )
    # ADD NEW STREAMLIT FLAG
    parser.add_argument(
        "--streamlit",
        action="store_true",
        help="Launch the Streamlit review UI for drafts"
    )
    # ... (rest of existing arguments)

    return parser



# ... (existing main function code)

    if args.streamlit:  # NEW CONDITION
        run_streamlit_app(args.out)  # RUN STREAMLIT APP
    else:
        # ... (existing logic for non-streamlit runs)






# ... (rest of the file)

# Add new streamlit_app.py file:
# src/gtm_command_center/streamlit_app.py
# (Full implementation would follow here)
