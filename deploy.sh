#!/bin/bash
gitbook pdf ./ ./book.pdf
cffconvert -ig -f zenodo -of .zenodo.json
python update_zenodo_guide.py
