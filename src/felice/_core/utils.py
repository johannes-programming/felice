import importlib.metadata
import importlib.resources
import os
import shutil
import string
import subprocess
import sys

import black
import bs4
import filelisting
import isort
import requests


def dict_match(a, b, /):
    a = dict(a)
    b = dict(b)
    keys = set(a.keys()) & set(b.keys())
    ans = all(a[k] == b[k] for k in keys)
    return ans


def fix_dependency(line, /):
    dependency = line.strip()
    chars = set(dependency)
    chars -= set(string.ascii_letters)
    chars -= set(string.digits)
    chars -= set("-_")
    if len(chars):
        return dependency
    version = _get_some_version(dependency)
    if version is None:
        return dependency
    dependency += ">=" + version
    return dependency


def prettify_html(file: str) -> None:
    # Read the HTML file
    with open(file, "r", encoding="utf-8") as stream:
        content = stream.read()

    # Parse the HTML content
    soup = bs4.BeautifulSoup(content, "html.parser")

    # Beautify the HTML
    formatter = bs4.formatter.HTMLFormatter(indent=4)
    beautified_html = soup.prettify(formatter=formatter)

    # Save the beautified HTML to a new file
    with open(file, "w", encoding="utf-8") as stream:
        stream.write(beautified_html)


def run_black(path):
    try:
        return black.main([path])
    except:
        pass


def run_html_prettifier(path):
    for file in filelisting.file_generator(path):
        filename = os.path.basename(file)
        ext = os.path.splitext(filename)
        if ext != ".html":
            continue


def run_isort():
    files = []
    walk = os.walk(os.getcwd())
    for root, dnames, fnames in walk:
        for fname in fnames:
            f = os.path.join(root, fname)
            files.append(f)
    for f in files:
        if os.path.splitext(f)[1] == ".py":
            isort.file(f)


def isdir(path):
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        raise ValueError
    return True


def isfile(path):
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        raise ValueError
    return True


def py(*args):
    args = [sys.executable, "-m"] + list(args)
    return subprocess.run(args)


def walk(path, *, recursively):
    if not os.path.exists(path):
        return (x for x in ())
    if not recursively:
        ans = os.listdir(path)
        ans = (os.path.join(path, n) for n in ans)
        ans = filter(os.path.isfile, ans)
        for f in ans:
            yield f
        return
    for root, dnames, fnames in os.walk(path):
        for fname in fnames:
            yield os.path.join(root, fname)


def _get_some_version(pkg, /):
    return _get_local_version(pkg) or _get_latest_version(pkg)


def _get_local_version(pkg, /):
    try:
        ans = importlib.metadata.version(pkg)
    except:
        return None
    url = "https://pypi.org/pypi/%s/%s" % (pkg, ans)
    r = requests.get(url)
    if r.status_code == 404:
        return None
    return ans


def _get_latest_version(pkg, /):
    url = "https://pypi.org/pypi/%s/json" % pkg
    try:
        r = requests.get(url)
        return r.json()["info"]["version"]
    except:
        return None
