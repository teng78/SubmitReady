from main import multiply


def test_intentional_failure() -> None:
    assert multiply(3, 4) == 13
