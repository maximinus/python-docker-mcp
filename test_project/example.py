import pytest


def capital_case(x):
    return x.capitalize()

def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'
    with pytest.raises(TypeError):
        capital_case(9)

if __name__ == '__main__':
    test_capital_case()
