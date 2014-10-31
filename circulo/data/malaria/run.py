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

DOWNLOAD_URL = 'http://danlarremore.com/bipartiteSBM/malariaData.zip'
DATA_DIR = "malariaData"

class MalariaData(CirculoData):

    def __download__(self):
        self.download_with_notes(DOWNLOAD_URL)


    def __prepare__(self):

        data = os.path.join(self.raw_data_path, DATA_DIR, "malaria.edgelist")
        mod_data = os.path.join(self.raw_data_path, DATA_DIR, "mod_malaria.edgelist")

        #we just need to remove the third column which has 1's in it
        #so igraph can read it as an edgelist
        with open(data, 'r') as f:
            with open(mod_data, 'w') as new:
                for line in f:
                    new.write(line[:-2] + '\n')

        G = igraph.load(mod_data)
        G.write_graphml(self.graph_path)

def main():
    databot = MalariaData("malaria")
    databot.get_graph()

if __name__ == "__main__":
    main()
