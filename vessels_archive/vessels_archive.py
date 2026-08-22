import sys
from datetime import datetime, timedelta
from pyspark.sql import SparkSession


def parse_date(date_str):
    """Utility to handle multiple date input formats."""
    date_str = date_str.replace("-", "/")
    return datetime.strptime(date_str, "%Y/%m/%d").date()


def main():
    # Verify positional arguments are provided
    if len(sys.argv) < 3:
        print("Usage: spark-submit script.py <start_date> <end_date>")
        print("Example: spark-submit script.py 2026/08/01 2026/08/30")
        sys.exit(1)

    start_date_input = sys.argv[1]
    end_date_input = sys.argv[2]

    # ============================================================
    # 1. Configuration
    # ============================================================
    BRONZE_BASE_PATH = "hdfs://bdss/bronze/vessels"
    ARCHIVE_DIR = f"{BRONZE_BASE_PATH}/archive2"
    ARCHIVE_FILE = f"{ARCHIVE_DIR}/vessels_archive.csv"

    # ============================================================
    # 2. Date Range
    # ============================================================
    start_date = parse_date(start_date_input)
    end_date = parse_date(end_date_input)

    # ============================================================
    # 3. Create Spark Session
    # ============================================================
    spark = (
        SparkSession.builder.appName("VesselsArchive")
        .master("local[1]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    # ============================================================
    # 4. Hadoop FileSystem Setup
    # ============================================================
    hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
    fs = spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(hadoop_conf)
    Path = spark.sparkContext._jvm.org.apache.hadoop.fs.Path

    # ============================================================
    # 5. Generate Date Paths
    # ============================================================
    input_paths = []
    current_date = start_date

    while current_date <= end_date:
        path = f"{BRONZE_BASE_PATH}/{current_date.strftime('%Y/%m/%d')}"
        input_paths.append(path)
        current_date += timedelta(days=1)

    print("=" * 70)
    print("VESSELS ARCHIVE JOB")
    print("=" * 70)
    print(f"Start date : {start_date}")
    print(f"End date   : {end_date}")
    print("\nInput paths:")

    for path in input_paths:
        print(path)

    # ============================================================
    # 6. Check Bronze Paths
    # ============================================================
    valid_csv_files = []

    print("\n" + "=" * 70)
    print("CHECKING BRONZE PATHS")
    print("=" * 70)

    for path in input_paths:
        date_path = Path(path)

        # Date directory doesn't exist
        if not fs.exists(date_path):
            print(f"[SKIP] Path not found: {path}")
            continue

        # Find CSV files
        csv_found = False

        for status in fs.listStatus(date_path):
            file_path = status.getPath()
            file_name = file_path.getName()

            if status.isFile() and file_name.lower().endswith(".csv"):
                valid_csv_files.append(str(file_path))
                csv_found = True
                print(f"[FOUND] {file_path}")

        # Directory exists but no CSV
        if not csv_found:
            print(f"[SKIP] No CSV files: {path}")

    print("\n" + "=" * 70)
    print(f"CSV FILES FOUND: {len(valid_csv_files)}")
    print("=" * 70)

    # ============================================================
    # 7. Stop if No CSV Files
    # ============================================================
    if not valid_csv_files:
        print("\nNo CSV files found.")
        print("Nothing to archive.")
        spark.stop()
        return

    # ============================================================
    # 8. Read New Bronze Data
    # ============================================================
    print("\nReading Bronze CSV files...")

    df_new = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .csv(valid_csv_files)
    )

    new_count = df_new.count()
    print(f"New records: {new_count}")

    if new_count == 0:
        print("CSV files contain no records.")
        print("Nothing to archive.")
        spark.stop()
        return

    print("\nSchema:")
    df_new.printSchema()

    print("\nSample data:")
    df_new.show(10, truncate=False)

    # ============================================================
    # 9. Create Archive Directory if Needed
    # ============================================================
    archive_dir_path = Path(ARCHIVE_DIR)
    archive_path = Path(ARCHIVE_FILE)

    if not fs.exists(archive_dir_path):
        print("\nArchive directory does not exist.")
        print("Creating archive directory...")
        fs.mkdirs(archive_dir_path)
        print("Archive directory created.")
    else:
        print("\nArchive directory already exists.")

    # ============================================================
    # 10. Create Temporary CSV
    # ============================================================
    temp_dir = f"{ARCHIVE_DIR}/_tmp_vessels_archive"
    temp_path = Path(temp_dir)

    print("\nCreating temporary CSV...")

    (
        df_new.coalesce(1)
        .write.mode("overwrite")
        .option("header", "true")
        .csv(temp_dir)
    )

    # ============================================================
    # 11. Find Spark Part File
    # ============================================================
    part_file = None

    for status in fs.listStatus(temp_path):
        file_path = status.getPath()
        file_name = file_path.getName()

        if (
            status.isFile()
            and file_name.startswith("part-")
            and file_name.endswith(".csv")
        ):
            part_file = file_path
            break

    if part_file is None:
        raise Exception("Spark did not generate a CSV part file.")

    print(f"Generated CSV: {part_file}")

    # ============================================================
    # 12 & 13. Archive File Handling (Create or Append)
    # ============================================================
    if not fs.exists(archive_path):
        print("\nArchive CSV does not exist.")
        print("Moving new CSV to archive...")

        success = fs.rename(part_file, archive_path)

        if not success:
            raise Exception("Failed to move CSV to archive.")

        print("Archive created successfully.")

    else:
        print("\nArchive CSV already exists.")
        print("Appending new records...")

        output_stream = fs.append(archive_path)
        input_stream = fs.open(part_file)

        # Skip header
        header = input_stream.readLine()
        print(f"Skipping header: {header}")

        # Append rows
        line = input_stream.readLine()
        while line is not None:
            output_stream.write((line + "\n").encode("utf-8"))
            line = input_stream.readLine()

        input_stream.close()
        output_stream.close()

        print("Records appended successfully.")

    # ============================================================
    # 14. Delete Temporary Directory
    # ============================================================
    if fs.exists(temp_path):
        fs.delete(temp_path, True)
        print("Temporary directory removed.")

    # ============================================================
    # 15. Final Verification
    # ============================================================
    print("\n" + "=" * 70)
    print("ARCHIVE COMPLETED")
    print("=" * 70)
    print(f"Records processed : {new_count}")
    print(f"Archive file      : {ARCHIVE_FILE}")
    print(f"Archive size      : {fs.getFileStatus(archive_path).getLen()} bytes")

    # ============================================================
    # 16. Delete Processed Bronze CSV Files
    # ============================================================
    print("\n" + "=" * 70)
    print("DELETING PROCESSED BRONZE FILES")
    print("=" * 70)

    for csv_file in valid_csv_files:
        csv_path = Path(csv_file)

        if fs.exists(csv_path):
            success = fs.delete(csv_path, False)
            if success:
                print(f"[DELETED] {csv_file}")
            else:
                print(f"[FAILED] Could not delete: {csv_file}")
        else:
            print(f"[SKIP] File no longer exists: {csv_file}")

    print("\nBronze cleanup completed.")

    # ============================================================
    # Cleanup Spark Session
    # ============================================================
    spark.stop()


if __name__ == "__main__":
    main()