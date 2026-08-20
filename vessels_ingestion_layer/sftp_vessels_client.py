import os
import re
import paramiko
import pandas as pd

from datetime import datetime, date
from .config import load_config

from .logger import Logger


logger = Logger(__name__)


# ============================================================
# Configuration
# ============================================================

config=load_config()
SFTP_HOST = config["sftp"]["host"]
SFTP_PORT = int(config["sftp"]["port"])
SFTP_USERNAME = config["sftp"]["username"]
SFTP_PASSWORD = config["sftp"]["password"]
SFTP_BASE_PATH = config["sftp"]["base_path"]

DATA_SOURCE = config["ingestion"]["data_source"]

TEMP_VESSEL_PATH = config["storage"]["temp_vessel_path"]


# ============================================================
# Create Temporary Directory
# ============================================================

def create_temp_directory():
    """
    Create the local temporary vessel directory.
    """

    try:

        os.makedirs(
            TEMP_VESSEL_PATH,
            exist_ok=True
        )

        logger.info(
            "Vessel temporary directory is ready: %s",
            TEMP_VESSEL_PATH
        )

    except OSError:

        logger.exception(
            "Failed to create vessel temporary directory: %s",
            TEMP_VESSEL_PATH
        )

        raise


# ============================================================
# SFTP Connection
# ============================================================

def create_sftp_connection():
    """
    Create and return an SFTP connection.
    """

    logger.info(
        "Connecting to SFTP server %s:%s",
        SFTP_HOST,
        SFTP_PORT
    )

    try:

        transport = paramiko.Transport(
            (SFTP_HOST, SFTP_PORT)
        )

        transport.connect(
            username=SFTP_USERNAME,
            password=SFTP_PASSWORD
        )

        sftp = paramiko.SFTPClient.from_transport(
            transport
        )

        logger.info(
            "Successfully connected to SFTP server"
        )

        return transport, sftp

    except Exception:

        logger.exception(
            "Failed to connect to SFTP server"
        )

        raise


# ============================================================
# List Files
# ============================================================

def list_files(
    sftp,
    remote_path
):
    """
    Return files available in a remote SFTP directory.
    """

    logger.info(
        "Listing files from SFTP path: %s",
        remote_path
    )

    try:

        files = sftp.listdir(
            remote_path
        )

        files = [
            file_name
            for file_name in files
            if not file_name.startswith(".")
        ]

        logger.info(
            "Found %d files in %s",
            len(files),
            remote_path
        )

        return files

    except Exception:

        logger.exception(
            "Failed to list files from %s",
            remote_path
        )

        raise


# ============================================================
# Extract Date from Filename
# ============================================================

def extract_file_date(file_name):
    """
    Extract date from vessel filename.

    Example:
        vessels_2026-08-17.csv

    Returns:
        datetime.date
        None if no date is found.
    """

    pattern = r"(\d{4}-\d{2}-\d{2})"

    match = re.search(
        pattern,
        file_name
    )

    if not match:

        logger.warning(
            "Could not extract date from filename: %s",
            file_name
        )

        return None

    try:

        file_date = datetime.strptime(
            match.group(1),
            "%Y-%m-%d"
        ).date()

    except ValueError:

        logger.warning(
            "Invalid date in filename: %s",
            file_name
        )

        return None

    logger.debug(
        "Extracted date %s from %s",
        file_date,
        file_name
    )

    return file_date


# ============================================================
# Find Vessel Files
# ============================================================

def get_vessel_files(
    sftp,
    start_date,
    end_date
):
    """
    Find vessel CSV files matching the requested date range.

    This function only discovers the files.
    It does NOT download their contents.
    """

    remote_path = (
        f"{SFTP_BASE_PATH}/vessels"
    )

    logger.info(
        "Searching for vessel files between %s and %s",
        start_date,
        end_date
    )

    files = list_files(
        sftp,
        remote_path
    )

    selected_files = []

    for file_name in files:

        # ----------------------------------------------------
        # Only vessel files
        # ----------------------------------------------------

        if not file_name.startswith(
            "vessels_"
        ):
            continue

        # ----------------------------------------------------
        # Only CSV files
        # ----------------------------------------------------

        if not file_name.endswith(
            ".csv"
        ):
            continue

        # ----------------------------------------------------
        # Extract date
        # ----------------------------------------------------

        file_date = extract_file_date(
            file_name
        )

        if file_date is None:
            continue

        # ----------------------------------------------------
        # Filter by date
        # ----------------------------------------------------

        if start_date <= file_date <= end_date:

            remote_file = (
                f"{remote_path}/{file_name}"
            )

            selected_files.append(
                {
                    "file_name": file_name,
                    "file_date": file_date,
                    "remote_path": remote_file
                }
            )

            logger.info(
                "Selected vessel file: %s",
                file_name
            )

    # --------------------------------------------------------
    # Sort by date
    # --------------------------------------------------------

    selected_files = sorted(
        selected_files,
        key=lambda x: x["file_date"]
    )

    logger.info(
        "Found %d matching vessel files",
        len(selected_files)
    )

    return selected_files


# ============================================================
# Add Ingestion Metadata
# ============================================================

def add_ingestion_metadata(
    local_path,
    ingestion_timestamp
):
    """
    Add ingestion metadata columns to a vessel CSV file.

    Columns added:

        data_source
        ingestion_timestamp
        ingestion_date
    """

    logger.info(
        "Adding ingestion metadata to: %s",
        local_path
    )

    try:

        # ----------------------------------------------------
        # Read CSV
        # ----------------------------------------------------

        df = pd.read_csv(
            local_path
        )

        # ----------------------------------------------------
        # Add data source
        # ----------------------------------------------------

        df["data_source"] = DATA_SOURCE

        # ----------------------------------------------------
        # Add ingestion timestamp
        # ----------------------------------------------------

        df["ingestion_timestamp"] = ingestion_timestamp

        # ----------------------------------------------------
        # Add ingestion date
        # ----------------------------------------------------

        df["ingestion_date"] = ingestion_timestamp.date()

        # ----------------------------------------------------
        # Save enriched CSV
        # ----------------------------------------------------

        df.to_csv(
            local_path,
            index=False
        )

        logger.info(
            "Successfully added ingestion metadata to: %s",
            local_path
        )

    except Exception:

        logger.exception(
            "Failed to add ingestion metadata to: %s",
            local_path
        )

        raise


# ============================================================
# Download Vessel Files
# ============================================================

def download_vessel_files(
    sftp,
    vessel_files,
    ingestion_timestamp
):
    """
    Download the actual vessel CSV files from SFTP
    into temp/vessel/ and add ingestion metadata.
    """

    create_temp_directory()

    downloaded_files = []

    for vessel_file in vessel_files:

        file_name = vessel_file[
            "file_name"
        ]

        remote_path = vessel_file[
            "remote_path"
        ]

        local_path = os.path.join(
            TEMP_VESSEL_PATH,
            file_name
        )

        logger.info(
            "Downloading vessel file: %s",
            file_name
        )

        try:

            # ------------------------------------------------
            # Download file
            # ------------------------------------------------

            sftp.get(
                remote_path,
                local_path
            )

            logger.info(
                "Successfully downloaded %s -> %s",
                remote_path,
                local_path
            )

            # ------------------------------------------------
            # Add ingestion metadata
            # ------------------------------------------------

            add_ingestion_metadata(
                local_path,
                ingestion_timestamp
            )

            # ------------------------------------------------
            # Add to downloaded files
            # ------------------------------------------------

            downloaded_files.append(
                local_path
            )

        except Exception:

            logger.exception(
                "Failed to download vessel file: %s",
                file_name
            )

            raise

    logger.info(
        "Successfully downloaded %d vessel files",
        len(downloaded_files)
    )

    return downloaded_files


# ============================================================
# Main
# ============================================================

def main(
    start_date,
    end_date
):
    """
    Discover and download vessel files.

    Files are stored in:

        temp/vessel/
    """

    transport = None
    sftp = None

    # --------------------------------------------------------
    # Create ingestion timestamp
    # --------------------------------------------------------

    ingestion_timestamp = datetime.now()

    logger.info(
        "Starting vessel ingestion: %s -> %s",
        start_date,
        end_date
    )

    logger.info(
        "Ingestion timestamp: %s",
        ingestion_timestamp
    )

    try:

        # ----------------------------------------------------
        # Create SFTP connection
        # ----------------------------------------------------

        transport, sftp = create_sftp_connection()

        # ----------------------------------------------------
        # Find matching files
        # ----------------------------------------------------

        vessel_files = get_vessel_files(
            sftp,
            start_date,
            end_date
        )

        # ----------------------------------------------------
        # Download actual files
        # ----------------------------------------------------

        downloaded_files = download_vessel_files(
            sftp,
            vessel_files,
            ingestion_timestamp
        )

        logger.info(
            "Vessel ingestion completed successfully"
        )

        return downloaded_files

    except Exception:

        logger.exception(
            "Vessel ingestion failed"
        )

        raise

    finally:

        # ----------------------------------------------------
        # Close SFTP connection
        # ----------------------------------------------------

        if sftp:
            sftp.close()

        if transport:
            transport.close()

        logger.info(
            "SFTP connection closed"
        )


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    start_date = date(
        2026,
        8,
        1
    )

    end_date = date(
        2026,
        8,
        23
    )

    downloaded_files = main(
        start_date,
        end_date
    )

    print("\nDownloaded files:")

    for file_path in downloaded_files:
        print(file_path)