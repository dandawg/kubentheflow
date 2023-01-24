
import pytest
import sys

sys.path.insert(1, '../')
from example_pipe.components.hello_comp import hello


# fixtures
@pytest.fixture
def name_doug():
    return "Doug"

@pytest.fixture
def name_alice3000():
    return "Alice3000"


# tests
def test_hello_doug(name_doug):
    assert hello(name_doug)[0] == "Hello Doug!"

def test_hello_alice(name_alice3000):
    e = f"The name '{name_alice3000}' is very odd. I can't handle it!"
    assert hello(name_alice3000)[0] == "Hello Alice3000!", e