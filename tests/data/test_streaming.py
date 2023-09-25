import tempfile
import time
from collections import defaultdict
from pathlib import Path

import pytest

from smoe.data.streaming import JsonlDataset, SubDirWeightedPackedJsonlDataset
from smoe.utils.io import load_jsonlines


def test_jsonl_dataset():
    def _get_num_iter(ds):
        num_ins = 0
        for _ in ds:
            num_ins += 1
        return num_ins

    filepath = "/mnt/petrelfs/zhutong/smoe/resources/redpajama/en_arxiv/head2k.jsonl"
    data = load_jsonlines(filepath)

    dataset = JsonlDataset(filepath, buffer_size=16)
    assert len(data) == _get_num_iter(dataset)

    num_skip = 50
    dataset = JsonlDataset(filepath, num_skip=num_skip)
    assert len(data) - num_skip == _get_num_iter(dataset)

    dataset = JsonlDataset(filepath, buffer_size=6)
    num_ins = 0
    for _ in dataset:
        num_ins += 1
        if num_ins == num_skip:
            break
    start_from = dataset.load_fh.tell()
    temp_dir = tempfile.mkdtemp()
    path = dataset.save_pretrained(temp_dir)

    new_dataset = JsonlDataset.from_pretrained(temp_dir)


@pytest.mark.skipif(
    Path("resources/data_test_with_task_type").exists(),
    reason="Test data dir not found",
)
def test_subdir_weighted_pack_with_type():
    dataset = SubDirWeightedPackedJsonlDataset(
        "resources/data_test_with_task_type",
        prob_map={"en_arxiv": 0.5, "en_book": 0.2, "en_c4": 0.3},
        buffer_size=1000,
        block_size=2048,
    )
    num_ds = 0
    num_src = defaultdict(lambda: 0)

    start = time.time()
    for ds in iter(dataset):
        num_ds += 1
        # print(num_ds, ds["src"])
        # num_src[ds["src"]] += 1
    time_span = time.time() - start
    print(num_ds)
    print(dict(num_src))
    print(f"Time (ins/s): {num_ds / time_span:.2f}" "")

    """
    block_size: -1
    {'en_arxiv': 400, 'en_c4': 244}
    Time (ins/s): 1075.88
    16.797501951600314 times faster than hf-datasets!

    block_size: 2048, buffer_size: 1000
    Time (ins/s): 283.53
    4.73023023023023 times faster than hf-datasets!
    """


if __name__ == "__main__":
    # test_jsonl_dataset()
    test_subdir_weighted_pack_with_type()
