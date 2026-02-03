import os
import shutil

import pytest

from skore_local_project.storage import DiskCacheStorage


class TestDiskCacheStorage:
    @pytest.fixture
    def storage(self, tmp_path):
        return DiskCacheStorage(tmp_path)

    def test_contains(self, storage):
        storage["<key1>"] = "<value1>"
        storage["<key2>"] = "<value2>"

        assert "<key1>" in storage
        assert "<key2>" in storage
        assert "<key3>" not in storage
