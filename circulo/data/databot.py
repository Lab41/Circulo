#!/usr/bin/env python
#
# Copyright (c) 2014 In-Q-Tel, Inc/Lab41, All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import igraph
from igraph import VertexCover
import urllib.request
import zipfile
import gzip

PRINT_PREFIX="[===DATA===]"

class CirculoData:

    def __init__(self, dataset_name):
        data_dir = os.path.dirname(__file__)
        graph_dir = os.path.join(data_dir, "GRAPHS")

        #make sure that the graph dir exists
        if not os.path.exists(graph_dir):
            os.mkdir(graph_dir)

        self.raw_data_path = os.path.join(data_dir,dataset_name, "raw")
        self.dataset_name = dataset_name
        self.graph_path = os.path.join(graph_dir, dataset_name+".graphml")

    def __download__(self):
        '''
        :data_dir  an existing directory where raw data should be stored

        Downloads data
        '''
        raise NotImplmentedError("function must be overridden")


    def __prepare__(self):
        '''
        :data_dir   an existing directory where raw data should be stored
        :graph_path path to serialized graph file
        :options    additional optionss
        '''
        raise NotImplementedError("function must be overridden")


    def get_ground_truth(self, G=None):
        '''
        Returns a VertexCover representing the ground truth for the given graph
        '''
        raise NotImplementedError("function must be overridden")

    def get_graph(self):
        '''
        Returns the graph loaded in memory
        '''

        if not os.path.exists(self.raw_data_path):
            os.mkdir(self.raw_data_path)
            self.__download__()

        if not os.path.exists(self.graph_path):
            self.__prepare__()

        return igraph.load(self.graph_path)


    def download_with_notes(self,url, progressbar=True, download_file=None):
        """
        Uses urllib to download data from URL. Saves the file_download.. Provides basic logging to stdout.

        :url            source url
        :file_downlaod  destination file path
        :progressbar    shows progress bar (default: true)

        """
        print(PRINT_PREFIX, "Downloading data from " + url + ".....")

        if download_file is None:
            download_file = os.path.basename(url)

        download_path = os.path.join(self.raw_data_path, download_file)

        try:
            if progressbar:
                urllib.request.urlretrieve(url, download_path, reporthook=progress)
            else:
                urllib.request.urlretrieve(url, download_path)
        except Exception as e:
            print(PRINT_PREFIX, "Data download failed -- make sure the url is still valid, and that urllib is properly installed.\n\n")
            raise(e)
        print(PRINT_PREFIX, "Download complete.")

        _unzip(download_path)


def _unzip(zip_path):
    '''
    Unzips the file at zip_path into the current directory

    :zip_path src of zip file
    '''

    if zipfile.is_zipfile(zip_path):
        try:
            z = zipfile.ZipFile(zip_path)
        except zipfile.BadZipFile as e:
            print(PRINT_PREFIX, "ZipFile error: {}".format(e))
            sys.exit(0)
        print(PRINT_PREFIX, "Extracting from zip...")
        z.extractall(path=os.path.dirname(zip_path))

    else:
        unzip_file = os.path.splitext(zip_path)[0]

        with gzip.open(zip_path,'rb') as infile:
            try:
                file_content = infile.read()
            except OSError as e:
                print(PRINT_PREFIX, "Neither gzip nor zipfile. No extraction necessary.")
                return

            with open(unzip_file, "wb") as f:
                print(PRINT_PREFIX, "Extracting from gzip...")
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

