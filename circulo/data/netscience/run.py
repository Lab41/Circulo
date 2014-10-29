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

import igraph
import os

from circulo.data.databot import CirculoData

DOWNLOAD_URL = 'http://www-personal.umich.edu/~mejn/netdata/netscience.zip'

class NetscienceData(CirculoData):

    def __download__(self):
        self.download_with_notes(DOWNLOAD_URL)

    def __prepare__(self):

        G = igraph.load(os.path.join(self.raw_data_path, "netscience.gml"))
        del G.vs['id'] #graphml uses the id field, so we must remove it
        G.write_graphml(self.graph_path)

def main():
    NetscienceData("netscience").get_graph()

if __name__ == "__main__":
    main()
