import pytest

import GUIopenCv as G

@pytest.mark.parametrize("input, expected_output",[
    ((0,0,0), (255,255,255))
])

def test_get_contrast_color(input, expected_output):
    output = G.get_contrast_color(input)
    assert output == expected_output