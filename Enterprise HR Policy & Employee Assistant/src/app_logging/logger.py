import logging
from pathlib import Path


# ---------------------------------------------------------
# Log directory
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# Log file
# ---------------------------------------------------------

LOG_FILE = LOG_DIR / "app.log"


# ---------------------------------------------------------
# Logger configuration
# ---------------------------------------------------------

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ---------------------------------------------------------
# Application logger
# ---------------------------------------------------------

app_logger = logging.getLogger("hr_assistant")

app_logger.setLevel(logging.INFO)


# ---------------------------------------------------------
# File handler
# ---------------------------------------------------------

if not app_logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        LOG_FORMAT,
        DATE_FORMAT
    )

    file_handler.setFormatter(formatter)

    app_logger.addHandler(file_handler)



def get_logger(name: str):

    return app_logger.getChild(name)