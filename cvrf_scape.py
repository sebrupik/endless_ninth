#!/usr/bin/env python3

import json
import wget
import xmltodict
import re
import requests
import sqlite3

CVRF_DETAIL_CREATE = "CREATE TABLE cvrf_detail (pk INTEGER UNIQUE, DocumentTitle TEXT, DocumentType TEXT," + \
                     "Summary INTEGER, AffectedProducts TEXT," + \
                     "VulnerableProducts TEXT, ConfirmedNotVulnerableProducts TEXT, Details TEXT, Workarounds TEXT," + \
                     "FixedSoftware TEXT, VulnerabilityPolicy TEXT, ExploitationAnnouncement TEXT, Source TEXT," + \
                     "ReferenceURL TEXT, PRIMARY KEY(pk AUTOINCREMENT))"
CVRF_DETAIL_INSERT = "INSERT INTO cvrf_detail(DocumentTitle, DocumentType, Summary, " \
                     "VulnerableProducts, ConfirmedNotVulnerableProducts, Details, Workarounds, FixedSoftware," \
                     "VulnerabilityPolicy, ExploitationAnnouncement, Source, ReferenceURL) " \
                     "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"
DOCUMENT_TRACKING_CREATE = "CREATE TABLE document_tracking (pk INTEGER UNIQUE, cvrf_pk INTEGER, revision INTEGER," + \
                           "date TEXT, description TEXT, PRIMARY KEY(pk AUTOINCREMENT))"
DOCUMENT_TRACKING_INSERT = "INSERT INTO document_tracking(pk_cvrf, dt_identification, status, version," \
                           "initial_release_date, current_release_date) VALUES(?,?,?,?,?,?)"
DOCUMENT_TRACKING_SELECT_BY_ID = "SELECT * FROM document_tracking WHERE dt_identification='{0}'"
REVISION_HISTORY_CREATE = ""
REVISION_HISTORY_INSERT = "INSERT INTO revision_history (dt_pk, number, date, description) VALUES(?,?,?,?)"

CREATE_VENDOR_IDS = "CREATE TABLE vendor_ids (pk INTEGER UNIQUE, Name TEXT, PRIMARY KEY(pk AUTOINCREMENT))"
CREATE_PRODUCT_NAMES = "CREATE TABLE product_names (pk INTEGER UNIQUE, ProductName TEXT," + \
                       "PRIMARY KEY(pk AUTOINCREMENT))"
CREATE_PRODUCT_IDS = "CREATE TABLE product_ids (pk INTEGER UNIQUE, CVRFPID TEXT, Name TEXT, FullName INTEGER," + \
                     "PRIMARY KEY(pk AUTOINCREMENT))"

HTML_REGEX = "^\s*<(a href=\")(?P<href>.*)\"\starget.*class=\"ng-binding\">(?P<name>.*)</a>$"

CVRF_URL = "https://tools.cisco.com/security/center/cvrfListing.x"
CVRF_LOCAL_URL = "/tmp/CVRF Repository.html"

def gather_cvrfs(con):
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
                    # print(json.dumps(xmltodict.parse(f2.read()), indent=4))
                    update_db_with_cvrf(con, xmltodict.parse(f2.read())["cvrfdoc"])


def docnotes_to_dict(input_list):
    d = dict()
    for e in input_list:
        d[e["@Title"]] = e

    print(json.dumps(d, indent=4))

    return d


def update_db_with_cvrf(con, cvrf_i):
    # print(json.dumps(cvrf_i, indent=4))

    d = docnotes_to_dict(cvrf_i["DocumentNotes"]["Note"])

    _cursor = con.cursor()
    _cursor.execute(CVRF_DETAIL_INSERT, (cvrf_i["DocumentTitle"], cvrf_i["DocumentType"], d["Summary"]["#text"],
                                         d["Vulnerable Products"]["#text"],
                                         d["Products Confirmed Not Vulnerable"]["#text"], d["Workarounds"]["#text"],
                                         d["Fixed Software"]["#text"], d["Vulnerability Policy"]["#text"],
                                         d["Exploitation and Public Announcements"]["#text"],
                                         d["Source"]["#text"], d["Legal Disclaimer"]["#text"],
                                         cvrf_i["DocumentReferences"]["Reference"][0]["URL"]))
    _cursor = con.cursor()

    # ["DocumentTracking"]
    dt = cvrf_i["DocumentTracking"]

    _cursor.execute(DOCUMENT_TRACKING_INSERT, ("-2", dt["Identification"]["ID"], dt["Status"], dt["Version"],
                                               dt["InitialReleaseDate"], dt["CurrentReleaseDate"]))
    con.commit()
    _cursor.execute(DOCUMENT_TRACKING_SELECT_BY_ID.format(dt["Identification"]["ID"]))
    row = _cursor.fetchone()

    for r in dt["RevisionHistory"]["Revision"]:
        print(r)
        _cursor.execute(REVISION_HISTORY_INSERT, (row[0], r["Number"], r["Date"], r["Description"]))
        con.commit()

    # ["DocumentNotes"]

    # ["DocumentReferences"]

    # ["ProductTree"]

    # ["Vulnerability"]



def main():
    con = sqlite3.connect('cvrfs.db')
    _cursor = con.cursor()
    _cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cvrf_detail'")
    row = _cursor.fetchone()

    if row is None:
        # build the tables
        con = sqlite3.connect('cvrfs.db')
        _cursor = con.cursor()
        _cursor.execute(CVRF_DETAIL_CREATE)
        _cursor.execute(DOCUMENT_TRACKING_CREATE)
        _cursor.execute(CREATE_VENDOR_IDS)
        _cursor.execute(CREATE_PRODUCT_NAMES)
        _cursor.execute(CREATE_PRODUCT_IDS)

    gather_cvrfs(con)


if __name__ == "__main__":
    main()
