# Copyright 2019 Jonathan Anderson
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
#
# SPDX-License-Identifier: Apache-2.0

import os
import yaml
import zipfile


def load_metadata(filename):
    """
    Load submission metadata from a Gradescope zip file or a metadata file.

    Returns the metadata as structured values and a function that can be used
    to open particular submissions by name.
    """

    if zipfile.is_zipfile(filename):
        meta_file, file_opener, dirname = load_from_zip(filename)

    else:
        meta_file, file_opener, dirname = load_from_file(filename)

    def get_file(name):
        return file_opener(os.path.join(dirname, name), 'rb')

    return (yaml.safe_load(meta_file), get_file)


def load_from_zip(filename):
    """
    Open a Gradescope .zip file that contains an assignment directory
    (e.g., `assignment_NNNNNN_export`), which contains both PDFs and
    the submission metadata file (`submission_metadata.yml`).

    Returns a tuple of the metadata YAML, a function that can be used to
    open file objects from the Zip file and the submission directory name.
    """

    assert(zipfile.is_zipfile(filename))

    meta = None
    dirname = None

    z = zipfile.ZipFile(filename, 'r')

    for info in z.infolist():
        if info.is_dir():
            dirname = info.filename

        elif 'submission_metadata' in info.filename:
            assert(dirname)     # directory must be specified first

            meta = z.open(info.filename)
            break;

    if not meta:
        raise ValueError(f'No submission metadata in {filename}')

    return (meta, z.open, dirname)


def load_from_file(filename):
    """
    The user may also specify a submission metadata file from an
    already-unzipped assignment submission directory.

    Returns a tuple of the metadata YAML, a function that can be used
    to open submission files and the submission directory name.
    """

    meta = open(filename, 'r')
    dirname = os.path.dirname(filename)

    return (meta, open, dirname)
