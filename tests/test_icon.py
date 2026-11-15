from pathlib import PurePosixPath

from runax_icons.icon import Icon

from .conftest import SQUARE


def icon(path: str) -> Icon:
    return Icon(PurePosixPath(path), SQUARE.encode())


def test_label_drops_vendor_prefixes_and_size_suffixes():
    assert icon("Arch_Compute/64/Arch_Amazon-EC2_64.svg").label({}) == "Amazon EC2"
    assert icon("Icons/ai/00028-icon-service-Batch-AI.svg").label({}) == "Batch AI"


def test_label_keeps_acronyms_and_uses_overrides():
    assert icon("Res_AWS-IoT_48_Light.svg").label({}) == "AWS IoT"
    assert icon("dbt.svg").label({"dbt": "dbt"}) == "dbt"


def test_size_variants_share_a_key_and_the_largest_ranks_highest():
    small, large = icon("Arch_AWS-Lambda_32.svg"), icon("Arch_AWS-Lambda_64.svg")
    assert small.key == large.key
    assert large.rank > small.rank


def test_unlabeled_beats_labeled_at_the_same_size():
    assert icon("unlabeled/pod.svg").rank > icon("labeled/pod.svg").rank


def test_file_id_is_stable_for_the_same_content():
    assert icon("a.svg").file_id == icon("b.svg").file_id
