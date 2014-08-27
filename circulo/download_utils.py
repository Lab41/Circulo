import urllib.request
import os
import zipfile
import gzip
import sys
import igraph as ig
from collections import defaultdict

def download_with_notes(url, filename, data_dir, progressbar=True):
    """
    Uses urllib to download data from URL. Saves the results in
    data_dir/FILENAME. Provides basic logging to stdout.
    """
    print("Downloading data from " + url + ".....")
    try:
        if progressbar:
            urllib.request.urlretrieve(url, os.path.join(data_dir, filename), progress)
        else:
            urllib.request.urlretrieve(url, os.path.join(data_dir, filename))
    except Exception as e:
        print("Data download failed -- make sure the url is still valid, and that urllib is properly installed.\n\n")
        raise(e)
    print("Download complete.")

    _unzip(data_dir, filename)

def _unzip(data_dir, filename):

    zip_path = os.path.join(data_dir, filename)

    if zipfile.is_zipfile(zip_path):
        try:
            z = zipfile.ZipFile(zip_path)
        except zipfile.BadZipFile as e:
            print("ZipFile error: {}".format(e))
            sys.exit(0)
        print("Extracting from zip...")
        z.extractall(path=data_dir)

    else:
        unzip_file = os.path.splitext(zip_path)[0]

        with gzip.open(zip_path,'rb') as infile:
            try:
                file_content = infile.read()
            except OSError as e:
                print("Neither gzip nor zipfile. No extraction necessary.") 
                return

            with open(unzip_file, "wb") as f:
                print("Extracting from gzip...")
                f.write(file_content)

def progress(blockNum, blockSize, totSize):
    """
    Provides an ascii progress bar that is 50 characters wide.
    totSize is the total size of the task, blockSize is the size
    of each block, and blockNum is the current block being worked on.

    For example:

    for i in range(100):
        progress(i + 1, 1, 100)
        sleep(1)

    will print a progress bar over 100 seconds.
    """
    downloaded = blockNum * blockSize
    per = min(100 * downloaded / totSize, 100)
    sys.stdout.write("\r%d%%" %per)
    for i in range(int(per / 2)):
        sys.stdout.write(".")
    for i in range(50 - int(per/2)):
        sys.stdout.write(" ")
    sys.stdout.write("# ")
    sys.stdout.flush()


def multigraph_to_weights(G):
    """
    Given a multigraph, coalesces all duplicate edges into a single
    weighted edge. Removes all other attributes. Assumes all edges
    are either weighted or unweighted.
    """
    seen = defaultdict(float)
    for e in G.es:
        try:
            weight = e['weight']
        except KeyError:
            weight = 1
        seen[e.tuple] += weight
    G.delete_edges(None)
    es = list(seen.keys())
    weights = list(seen.values())
    G.add_edges(es)
    G.es['weight'] = weights


