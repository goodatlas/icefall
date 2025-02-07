#!/usr/bin/env python3
# Copyright    2021  Xiaomi Corp.        (authors: Fangjun Kuang)
# Copyright    2021  Atlaslabs           (author: Lucas Jo)
#
# See ../../../../LICENSE for clarification regarding multiple authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
This file downloads the following Zeroth LM files:

    - zeroth.lm.fg.arpa.gz,
    - zeroth.lm.tg.arpa.gz,
    - zeroth.lm.tgmed.arpa.gz,
    - zeroth.lm.tgsmall.arpa.gz,
    - zeroth_lexicon,
    - zeroth_morfessor.seg

from AWS s3 
and save them in the user provided directory.

Files are not re-downloaded if they already exist.

Usage:
    ./local/download_lm.py --out-dir ./download/lm
"""

import argparse
import gzip
import logging
import os
import shutil
import tarfile
from pathlib import Path

from lhotse.utils import urlretrieve_progress
from tqdm.auto import tqdm
from zeroth_downloader import ZerothSpeechDownloader


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=str, help="Output directory.")

    args = parser.parse_args()
    return args


def main(out_dir: str):
    zeroth_dl = ZerothSpeechDownloader()
    out_dir = Path(out_dir)

    files_to_download = (
        "zeroth.lm.fg.arpa.gz",
        "zeroth.lm.tg.arpa.gz",
        "zeroth.lm.tgmed.arpa.gz",
        "zeroth.lm.tgsmall.arpa.gz",
        "zeroth_lexicon",
        "zeroth_morfessor.seg"
    )

    for f in tqdm(files_to_download, desc="Downloading ZerothSpeech LM files"):
        filename = out_dir / f
        if filename.is_file() is False:
            logging.info(f"{filename} - downloading")
            zeroth_dl.download(str(f), str(filename))
        else:
            logging.info(f"{filename} already exists - skipping")

        if ".gz" in str(filename):
            unzipped = Path(os.path.splitext(filename)[0])
            if unzipped.is_file() is False:
                with gzip.open(filename, "rb") as f_in:
                    with open(unzipped, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                logging.info(f"{unzipped} already exist - skipping")


if __name__ == "__main__":
    formatter = (
        "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    )

    logging.basicConfig(format=formatter, level=logging.INFO)

    args = get_args()
    logging.info(f"out_dir: {args.out_dir}")

    main(out_dir=args.out_dir)
