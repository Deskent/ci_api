import pytest

from schemas.user_schema import slice_phone_to_format


@pytest.mark.server
def test_slice_phone_to_format():
    tel = '+7 (921) 744-8833'
    result = slice_phone_to_format(tel)
    assert len(result) == 10
    assert result.isdigit()
