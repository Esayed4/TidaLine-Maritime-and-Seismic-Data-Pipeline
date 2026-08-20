import os
import re
import paramiko

from datetime import datetime
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
TEMP_DIR  = config["storage"]["temp_vessel_path"]




SOURCE_DIR = "/data/vessels"
ARCHIVE_DIR = "/data/archive"


# ============================================================
# Cleanup and Archive
# ============================================================

def cleanup_and_archive(start_date, end_date):

    # ========================================================
    # Validate date range
    # ========================================================

    if start_date > end_date:
        raise ValueError(
            f"Start date {start_date} cannot be after "
            f"end date {end_date}"
        )

    logger.info(
        f"Starting cleanup and archive: "
        f"{start_date} -> {end_date}"
    )

    # ========================================================
    # Connect to SFTP
    # ========================================================

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

    try:

        # ====================================================
        # Create archive directory if it doesn't exist
        # ====================================================

        try:

            sftp.stat(ARCHIVE_DIR)

        except FileNotFoundError:

            sftp.mkdir(ARCHIVE_DIR)

            logger.info(
                f"Created archive directory: {ARCHIVE_DIR}"
            )

        # ====================================================
        # Get files from SFTP
        # ====================================================

        files = sftp.listdir(SOURCE_DIR)

        logger.info(
            f"Found {len(files)} file(s) in {SOURCE_DIR}"
        )

        processed_count = 0

        # ====================================================
        # Process files
        # ====================================================

        for filename in files:

            # Expected filename:
            # vessels_2026-08-17.csv

            match = re.match(
                r"^vessels_(\d{4}-\d{2}-\d{2})\.csv$",
                filename
            )

            # ------------------------------------------------
            # Skip files that don't match the pattern
            # ------------------------------------------------

            if not match:

                logger.info(
                    f"Skipping invalid file: {filename}"
                )

                continue

            # ------------------------------------------------
            # Extract date from filename
            # ------------------------------------------------

            file_date = datetime.strptime(
                match.group(1),
                "%Y-%m-%d"
            ).date()

            logger.info(
                f"File: {filename} | "
                f"File date: {file_date}"
            )

            # ------------------------------------------------
            # Check date range
            # Both start_date and end_date are inclusive
            # ------------------------------------------------

            if not (start_date <= file_date <= end_date):

                logger.info(
                    f"Skipping {filename}. "
                    f"Date {file_date} is outside range "
                    f"{start_date} -> {end_date}"
                )

                continue

            logger.info(
                f"Processing file: {filename}"
            )

            # =================================================
            # Delete local temp file
            # =================================================

            temp_file = os.path.join(
                TEMP_DIR,
                filename
            )

            if os.path.exists(temp_file):

                os.remove(temp_file)

                logger.info(
                    f"Deleted temp file: {temp_file}"
                )

            else:

                logger.info(
                    f"Temp file not found: {temp_file}"
                )

            # =================================================
            # Archive SFTP source file
            # =================================================

            source_path = f"{SOURCE_DIR}/{filename}"

            archive_path = f"{ARCHIVE_DIR}/{filename}"

            # -------------------------------------------------
            # Avoid overwriting an existing archive file
            # -------------------------------------------------

            try:

                sftp.stat(archive_path)

                logger.info(
                    f"Archive file already exists: "
                    f"{archive_path}"
                )

                # Remove the source file because it has
                # already been archived previously.
                sftp.remove(source_path)

                logger.info(
                    f"Removed duplicate source file: "
                    f"{source_path}"
                )

            except FileNotFoundError:

                sftp.rename(
                    source_path,
                    archive_path
                )

                logger.info(
                    f"Archived: "
                    f"{source_path} -> {archive_path}"
                )

            processed_count += 1

        # ====================================================
        # Summary
        # ====================================================

        logger.info(
            f"Cleanup and archive completed successfully. "
            f"Processed {processed_count} file(s). "
            f"Date range: {start_date} -> {end_date}"
        )

    finally:

        # ====================================================
        # Close SFTP connection
        # ====================================================

        sftp.close()
        transport.close()

        logger.info(
            "SFTP connection closed."
        )