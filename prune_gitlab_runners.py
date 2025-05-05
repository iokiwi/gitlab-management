#!/usr/bin/env python3

from pprint import pprint
import requests
import os
import sys

from dotenv import load_dotenv


def main(gitlab_token):
    resp = requests.get(  # nosec B113
        "https://gitlab.com/api/v4/runners",
        headers={"PRIVATE-TOKEN": gitlab_token},
        params={"per_page": 100},
    )

    if not resp.ok:
        print(resp.status_code, resp.text)
        sys.exit()

    runners = resp.json()

    deleted = 0
    online = 0

    for runner in runners:
        if not runner["status"] == "online":
            print(
                "Deleting: {} {} [{}]".format(
                    runner["id"], runner["description"], runner["status"]
                )
            )

            r = requests.delete(  # nosec B113
                "https://gitlab.com/api/v4/runners/{}".format(runner["id"]),
                headers={"PRIVATE-TOKEN": gitlab_token},
            )

            if r.ok:
                print("Deleted")
                deleted += 1
            else:
                print("Failedto delete runner: ")
                pprint(runner)
        else:
            online += 1

    print("Deleted: {}/{}".format(deleted, len(runners)))
    print("Online: {}".format(online))


if __name__ == "__main__":
    # Your personal access token
    # https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

    load_dotenv()

    gitlab_token = os.environ.get("GITLAB_TOKEN")

    if gitlab_token is None:
        print("Gitlab token is not set")
        print("Please set GITLAB_TOKEN in your environment")
    else:
        main(gitlab_token)
