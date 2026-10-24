#!/usr/bin/env python3
"""Build source.json (AltStore format, which Feather reads) from apps.json.

Each app's versions are its newest GitHub releases whose tag starts with
`tagPrefix` and that carry `asset`. Release names end in "<version> (build <n>)".

Usage: GITHUB_TOKEN=... build_source.py [apps.json] [source.json]
"""
import json
import os
import re
import sys
import urllib.request

KEEP = 5
SOURCE_URL = "https://raw.githubusercontent.com/elabx-org/feather-source/main/source.json"


def releases(repo):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases?per_page=50",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def versions(app):
    found = []
    for release in releases(app["repo"]):
        if release["draft"] or not release["tag_name"].startswith(app["tagPrefix"]):
            continue
        asset = next((a for a in release["assets"] if a["name"] == app["asset"]), None)
        match = re.search(r"(\d+\.\d+\.\d+) \(build (\d+)\)", release["name"] or "")
        if not asset or not match:
            continue
        found.append({
            "version": match.group(1),
            "buildVersion": match.group(2),
            "date": release["published_at"],
            "localizedDescription": f"Build {match.group(2)} ({release['tag_name']})",
            "downloadURL": asset["browser_download_url"],
            "size": asset["size"],
            "minOSVersion": app["minOSVersion"],
        })
    found.sort(key=lambda v: int(v["buildVersion"]), reverse=True)
    return found[:KEEP]


def entry(app):
    listed = versions(app)
    if not listed:
        raise SystemExit(f"{app['repo']}: no releases with {app['asset']}")
    newest = listed[0]
    fields = ("name", "bundleIdentifier", "developerName", "subtitle",
              "localizedDescription", "iconURL", "tintColor")
    return {
        **{k: app[k] for k in fields},
        "versions": listed,
        # Single-version fields, for older AltStore-format readers
        "version": newest["version"],
        "versionDate": newest["date"],
        "versionDescription": newest["localizedDescription"],
        "downloadURL": newest["downloadURL"],
        "size": newest["size"],
        "appPermissions": {"entitlements": [], "privacy": {}},
    }


def main():
    apps_path = sys.argv[1] if len(sys.argv) > 1 else "apps.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "source.json"
    with open(apps_path) as f:
        apps = json.load(f)
    source = {
        "name": "elabx",
        "identifier": "org.elabx.source",
        "subtitle": "elabx apps for sideloading",
        "sourceURL": SOURCE_URL,
        "website": "https://github.com/elabx-org/feather-source",
        "apps": [entry(app) for app in apps],
        "news": [],
    }
    with open(out_path, "w") as f:
        json.dump(source, f, indent=2)
        f.write("\n")
    for app in source["apps"]:
        print(f"{app['name']}: {app['version']} ({app['versions'][0]['buildVersion']})")


if __name__ == "__main__":
    main()
