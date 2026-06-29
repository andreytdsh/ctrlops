import pytest

from ctrlops.utils.validators import validate_domain


def test_domain_validation_accepts_valid_domain():
    assert validate_domain("Example.COM.") == "example.com"


def test_domain_validation_rejects_invalid_domain():
    with pytest.raises(ValueError):
        validate_domain("bad domain")
