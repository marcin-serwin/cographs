#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
npm i pyright@1.1.51
mkdir typings
cd typings
git clone git@github.com:marcin-serwin/networkx-stubs.git
ln -s networkx-stubs/networkx-stubs networkx
