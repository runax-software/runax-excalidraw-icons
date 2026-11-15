from pathlib import PurePosixPath

from runax_icons.excalidraw import ElementFactory
from runax_icons.excalidraw.elements import LABEL_GAP, wrap_label
from runax_icons.icon import Icon

from .conftest import SQUARE


def test_short_labels_stay_on_one_line():
    assert wrap_label("PostgreSQL") == "PostgreSQL"


def test_long_labels_wrap_onto_two_balanced_lines_at_most():
    wrapped = wrap_label("Amazon Aurora Trusted Language Extensions for PostgreSQL")
    assert wrapped.count("\n") == 1
    first, second = wrapped.split("\n")
    assert abs(len(first) - len(second)) < 10


def test_vendor_words_stay_with_the_next_word():
    assert wrap_label("AWS Elastic Beanstalk") == "AWS Elastic\nBeanstalk"
    assert wrap_label("Amazon CodeCatalyst") == "Amazon CodeCatalyst"  # never "Amazon" alone


def test_icon_box_sets_image_size_and_caption_position():
    icon = Icon(PurePosixPath("Res_Thing_48.svg"), SQUARE.encode())
    image, caption = ElementFactory(now=0).icon(icon, "Thing", box=48)
    assert (image.width, image.height) == (48, 48)
    assert caption.y == 48 + LABEL_GAP
