import requests


NAMENODES = [
    "http://master1:9870",
    "http://master2:9870",
]


def get_active_webhdfs_url():

    for namenode in NAMENODES:

        try:
            print(f"Checking {namenode}")

            response = requests.get(
                f"{namenode}/jmx",
                params={
                    "qry": "Hadoop:service=NameNode,name=NameNodeStatus"
                },
                timeout=3,
            )

            print(f"HTTP status: {response.status_code}")
            print(f"Response: {response.text}")

            response.raise_for_status()

            data = response.json()

            state = data["beans"][0]["State"]

            print(f"State: {state}")

            if state.lower() == "active":
                url = f"{namenode}/webhdfs/v1"
                print(f"ACTIVE NameNode: {url}")
                return url

        except Exception as e:
            print(f"ERROR checking {namenode}: {type(e).__name__}: {e}")

    return None