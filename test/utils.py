import os

import pytest


def read_response_file(filename):
    return open(os.path.join(pytest.SAMPLE_DATA_PATH, "music", filename)).read()
