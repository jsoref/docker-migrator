#!/usr/bin/python
import requests
import sys
import os


# get a list of tags present in the v2 registry for
# a given image
def get_v2_tags(image_name):
    try:
        response = requests.get(
            "http://%s/v2/%s/tags/list"
            % (os.environ.get("V2_REGISTRY"), image_name)).json()
        return response["tags"]
    except:
        return []


# get all the builds for a repository from the image registry
def get_builds(image_name):
    response = requests.get(
        "http://%s/v1/repositories/%s/tags"
        % (os.environ.get("V1_REGISTRY"), image_name)).json()
    builds = {}
    for (tagname, hashname) in response.iteritems():
        if builds.get(hashname):
            builds[hashname]["tags"].append(tagname)
        else:
            builds[hashname] = {
                "image": image_name,
                "build_hash": hashname,
                "tags": [tagname]
            }
    return builds.values()


# check whether the hash of the build in the v2 registry matches
# the hash of the tagged build in the v1 registry
def needsUpdating(image, tag, hashvalue):
    try:
        response = requests.get(
            "http://%s/v2/%s/manifests/%s" %
            (os.environ.get("V2_REGISTRY"), image, tag)).json()
        if response["history"][0]:
            if hashvalue in response["history"][0]["v1Compatibility"]:
                return False
        raise Exception("build not found")
    except(Exception):
        return True


def main():
    if len(sys.argv) < 2:
        print("No repo specified.")
        sys.exit(1)

    repo = sys.argv[1]

    migrated_tags = get_v2_tags(repo)
    builds = get_builds(repo)

    for build in builds:
        # make a copy since we'll be removing elements below
        tags = list(build["tags"])
        for tag in tags:
            if tag in migrated_tags:
                if not needsUpdating(repo, tag, build["build_hash"]):
                    build["tags"].remove(tag)

    for build in builds:
        for tag in build["tags"]:
            print build["image"] + ":" + tag

if __name__ == "__main__":
    main()
