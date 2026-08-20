import os
import re

import requests

from datetime import date, datetime

from .logger import Logger


logger = Logger(__name__)


# ============================================================
# Configuration
# ============================================================

WEBHDFS_BASE_URL = "http://master1:9870/webhdfs/v1"
HDFS_USER = "user"

LOCAL_VESSELS_PATH = "/opt/airflow/dags/temp/vessel" ## take care
HDFS_VESSELS_PATH = "/bronze/vessels"


# ============================================================
# HDFS Functions
# ============================================================

def create_hdfs_directory(hdfs_path: str) -> None:
    """
    Create an HDFS directory if it does not already exist.

    MKDIRS creates the directory and any missing parent
    directories.
    """

    url = f"{WEBHDFS_BASE_URL}{hdfs_path}"

    params = {
        "op": "MKDIRS",
        "user.name": HDFS_USER,
    }

    logger.debug(
        f"Preparing to create HDFS directory: {hdfs_path}"
    )

    try:
        response = requests.put(
            url,
            params=params
        )

        response.raise_for_status()

        logger.info(
            f"HDFS directory is ready: {hdfs_path}"
        )

    except requests.RequestException as exc:
        logger.error(
            f"Failed to create HDFS directory "
            f"{hdfs_path}: {exc}"
        )
        raise


def upload_file_to_hdfs(
    local_file_path: str,
    hdfs_file_path: str
) -> None:
    """
    Upload a local file to HDFS using WebHDFS.
    """

    url = f"{WEBHDFS_BASE_URL}{hdfs_file_path}"

    params = {
        "op": "CREATE",
        "user.name": HDFS_USER,
        "overwrite": "true",
    }

    logger.debug(
        f"Preparing to upload: "
        f"{local_file_path} -> {hdfs_file_path}"
    )

    try:

        with open(local_file_path, "rb") as file:

            response = requests.put(
                url,
                params=params,
                data=file,
                allow_redirects=True
            )

        response.raise_for_status()

        logger.info(
            f"Successfully uploaded: "
            f"{hdfs_file_path}"
        )

    except FileNotFoundError:
        logger.error(
            f"Local file was not found: "
            f"{local_file_path}"
        )
        raise

    except PermissionError:
        logger.error(
            f"Permission denied while reading: "
            f"{local_file_path}"
        )
        raise

    except requests.RequestException as exc:
        logger.error(
            f"Failed to upload file "
            f"{local_file_path} to "
            f"{hdfs_file_path}: {exc}"
        )
        raise


# ============================================================
# File Functions
# ============================================================

def extract_date_from_filename(
    filename: str
) -> date | None:
    """
    Extract the date from a vessel filename.

    Example:
        vessels_2026-08-17.csv

    Returns:
        date object if a valid date is found,
        otherwise None.
    """

    logger.debug(
        f"Extracting date from filename: {filename}"
    )

    match = re.search(
        r"(\d{4}-\d{2}-\d{2})",
        filename
    )

    if not match:

        logger.warning(
            f"No date found in filename: {filename}"
        )

        return None

    try:

        file_date = datetime.strptime(
            match.group(1),
            "%Y-%m-%d"
        ).date()

        logger.debug(
            f"Extracted date {file_date} "
            f"from filename: {filename}"
        )

        return file_date

    except ValueError:

        logger.warning(
            f"Invalid date in filename: {filename}"
        )

        return None


def get_files_in_date_range(
    start_date: date,
    end_date: date
) -> list[str]:
    """
    Get CSV files from the local vessels directory
    within the specified date range.
    """

    logger.debug(
        f"Scanning directory: {LOCAL_VESSELS_PATH}"
    )

    if not os.path.exists(LOCAL_VESSELS_PATH):

        logger.error(
            f"Local vessels directory does not exist: "
            f"{LOCAL_VESSELS_PATH}"
        )

        raise FileNotFoundError(
            LOCAL_VESSELS_PATH
        )

    files = []

    for filename in os.listdir(LOCAL_VESSELS_PATH):

        # ----------------------------------------------------
        # Skip non-CSV files
        # ----------------------------------------------------

        if not filename.endswith(".csv"):

            logger.debug(
                f"Skipping non-CSV file: {filename}"
            )

            continue

        # ----------------------------------------------------
        # Extract date
        # ----------------------------------------------------

        file_date = extract_date_from_filename(
            filename
        )

        if file_date is None:

            logger.warning(
                f"Skipping file because its date "
                f"could not be determined: {filename}"
            )

            continue

        # ----------------------------------------------------
        # Check date range
        # ----------------------------------------------------

        if start_date <= file_date <= end_date:

            logger.debug(
                f"File selected: {filename} "
                f"(date: {file_date})"
            )

            files.append(filename)

        else:

            logger.debug(
                f"File outside requested date range: "
                f"{filename}"
            )

    # --------------------------------------------------------
    # Sort files
    # --------------------------------------------------------

    files = sorted(files)

    if not files:

        logger.warning(
            f"No vessel CSV files found between "
            f"{start_date} and {end_date}"
        )

    else:

        logger.info(
            f"Found {len(files)} vessel files "
            f"between {start_date} and {end_date}"
        )

    return files


# ============================================================
# Main Function
# ============================================================

def upload_vessels_to_hdfs(
    start_date: date,
    end_date: date
) -> list[str]:
    """
    Upload vessel CSV files from the local temp directory
    to HDFS for the specified date range.

    HDFS structure:

        /bronze/vessels/
            YYYY/
                MM/
                    DD/
                        file.csv

    Example:

        /bronze/vessels/2026/08/17/
            vessels_2026-08-17.csv

    Returns:
        List of uploaded HDFS file paths.
    """

    logger.info(
        f"Starting vessel upload: "
        f"{start_date} -> {end_date}"
    )

    # ========================================================
    # Validate date range
    # ========================================================

    if start_date > end_date:

        logger.error(
            f"Invalid date range: "
            f"start_date ({start_date}) is after "
            f"end_date ({end_date})"
        )

        raise ValueError(
            "start_date must be less than or equal to end_date"
        )

    # ========================================================
    # Make sure base HDFS directory exists
    # ========================================================

    create_hdfs_directory(
        HDFS_VESSELS_PATH
    )

    # ========================================================
    # Get files
    # ========================================================

    files = get_files_in_date_range(
        start_date=start_date,
        end_date=end_date
    )

    uploaded_files = []

    # ========================================================
    # Upload files
    # ========================================================

    for filename in files:

        logger.debug(
            f"Processing vessel file: {filename}"
        )

        # ----------------------------------------------------
        # Local file path
        # ----------------------------------------------------

        local_file_path = os.path.join(
            LOCAL_VESSELS_PATH,
            filename
        )

        # ----------------------------------------------------
        # Extract file date
        # ----------------------------------------------------

        file_date = extract_date_from_filename(
            filename
        )

        if file_date is None:

            logger.warning(
                f"Skipping file because date "
                f"could not be extracted: {filename}"
            )

            continue

        # ----------------------------------------------------
        # Build HDFS directory
        #
        # /bronze/vessels/YYYY/MM/DD
        # ----------------------------------------------------

        hdfs_directory = (
            f"{HDFS_VESSELS_PATH}/"
            f"{file_date.year}/"
            f"{file_date.month:02d}/"
            f"{file_date.day:02d}"
        )

        # ----------------------------------------------------
        # Create date partition directory
        # ----------------------------------------------------

        create_hdfs_directory(
            hdfs_directory
        )

        # ----------------------------------------------------
        # Build final HDFS file path
        #
        # /bronze/vessels/YYYY/MM/DD/file.csv
        # ----------------------------------------------------

        hdfs_file_path = (
            f"{hdfs_directory}/{filename}"
        )

        # ----------------------------------------------------
        # Upload file
        # ----------------------------------------------------

        upload_file_to_hdfs(
            local_file_path=local_file_path,
            hdfs_file_path=hdfs_file_path
        )

        # ----------------------------------------------------
        # Store uploaded path
        # ----------------------------------------------------

        uploaded_files.append(
            hdfs_file_path
        )

    # ========================================================
    # Final logging
    # ========================================================

    if uploaded_files:

        logger.info(
            f"Vessel upload completed successfully. "
            f"Uploaded {len(uploaded_files)} files."
        )

    else:

        logger.warning(
            "Vessel upload completed, "
            "but no files were uploaded."
        )

    return uploaded_files