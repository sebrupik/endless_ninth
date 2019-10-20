#!/usr/bin/env python3

import json
import wget
import xmltodict
import re
import requests
import sqlite3

CREATE_CVRF_DETAIL = "CREATE TABLE cvrf_detail (pk INTEGER UNIQUE, DocumentTitle TEXT, DocumentType TEXT," + \
                     "InitialReleaseDate TEXT, CurrentReleaseDate TEXT, Summary INTEGER, AffectedProducts TEXT," + \
                     "VulnerableProducts TEXT, ConfirmedNotVulnerableProducts TEXT, Details TEXT, Workarounds TEXT," + \
                     "FixedSoftware TEXT, VulnerabilityPolicy TEXT, ExploitationAnnouncement TEXT, Source TEXT," + \
                     "ReferenceURL TEXT, PRIMARY KEY(pk AUTOINCREMENT))"
CREATE_DOCUMENT_TRACKING = "CREATE TABLE document_tracking (pk INTEGER UNIQUE, cvrf_pk INTEGER, revision INTEGER," + \
                           "date TEXT, description TEXT, PRIMARY KEY(pk AUTOINCREMENT))"
CREATE_VENDOR_IDS = "CREATE TABLE vendor_ids (pk INTEGER UNIQUE, Name TEXT, PRIMARY KEY(pk AUTOINCREMENT))"
CREATE_PRODUCT_NAMES = "CREATE TABLE product_names (pk INTEGER UNIQUE, ProductName TEXT," + \
                       "PRIMARY KEY(pk AUTOINCREMENT))"
CREATE_PRODUCT_IDS = "CREATE TABLE product_ids (pk INTEGER UNIQUE, CVRFPID TEXT, Name TEXT, FullName INTEGER," + \
                     "PRIMARY KEY(pk AUTOINCREMENT))"

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


#def update_db_with_cvrf():


def main():
    con = sqlite3.connect('cvrfs.db')
    _cursor = con.cursor()
    _cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cvrf_detail'")
    row = _cursor.fetchone()

    if row is None:
        # build the tables
        con = sqlite3.connect('cvrfs.db')
        _cursor = con.cursor()
        _cursor.execute(CREATE_CVRF_DETAIL)
        _cursor.execute(CREATE_DOCUMENT_TRACKING)
        _cursor.execute(CREATE_VENDOR_IDS)
        _cursor.execute(CREATE_PRODUCT_NAMES)
        _cursor.execute(CREATE_PRODUCT_IDS)

    gather_cvrfs()


if __name__ == "__main__":
    main()
