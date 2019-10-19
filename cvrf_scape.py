#!/usr/bin/env python3

import json
import wget
import xmltodict
import re
import requests


HTML_REGEX = "^\s*<(a href=\")(?P<href>.*)\"\starget.*class=\"ng-binding\">(?P<name>.*)</a>$"

CVRF_URL = "https://tools.cisco.com/security/center/cvrfListing.x"
CVRF_LOCAL_URL = "/tmp/CVRF Repository.html"

def gather_cvrfs():
    #r = requests.get(CVRF_LOCAL_URL)
    #print(r.text)
    with open(CVRF_LOCAL_URL) as f:
        # print(f.read())
        for line in f.read().splitlines():
            print(line)
            match = re.match(HTML_REGEX, line)
            if match:
                print("---- {0}".format(line))
                print("Downloading: {0}".format(match.group("name")))
                filename = wget.download(match.group("href"), "./output")
                with open(filename) as f2:
                    print(json.dumps(xmltodict.parse(f2.read()), indent=4))


def main():
    gather_cvrfs()


if __name__ == "__main__":
    main()
