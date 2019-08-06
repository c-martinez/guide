#!/bin/bash
gitbook pdf ./ ./book.pdf
python update_zenodo_guide.py
