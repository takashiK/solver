import pytest

from solver import Number_selector

def test_number_selector_setValue():
    selector = Number_selector((0,0))
    assert selector.value() is None
    for i in range(1,10):
        selector.setValue(i)
        assert selector.value() == i
    selector.setValue(None)
    assert selector.value() is None

def test_number_selector_available():
    selector = Number_selector((0,0))
    assert selector.available() == [1,2,3,4,5,6,7,8,9]

    for i in range(1,10):
        selector.setValue(i)
        assert selector.available() == [i]

    selector.setValue(None)
    selector.disable([1])
    assert selector.available() == [2,3,4,5,6,7,8,9]
    selector.disable([1])
    assert selector.available() == [2,3,4,5,6,7,8,9]
    selector.disable([5,6])
    assert selector.available() == [2,3,4,7,8,9]
    selector.disable([5,6,2])
    assert selector.available() == [3,4,7,8,9]
    selector.disable([3,4,9])
    assert selector.available() == [7,8]
    selector.disable([7,8])
    assert selector.available() == []

def test_number_selector_reset_solve():
    selector = Number_selector((0,0))
    assert selector.available() == [1,2,3,4,5,6,7,8,9]
    selector.disable([5,6,2])
    assert selector.available() == [1,3,4,7,8,9]
    selector.reset_solve()
    assert selector.available() == [1,2,3,4,5,6,7,8,9]
    selector.setValue(3)
    assert selector.available() == [3]
    selector.reset_solve()
    assert selector.available() ==  [1,2,3,4,5,6,7,8,9]
    selector.setValue(3)
    selector.selected = True
    selector.reset_solve()
    assert selector.available() == [3]

def test_number_selector_clear_solve():
    selector = Number_selector((0,0))
    assert selector.available() == [1,2,3,4,5,6,7,8,9]
    selector.disable([5,6,2])
    assert selector.available() == [1,3,4,7,8,9]
    selector.clear_solve()
    assert selector.available() == [1,2,3,4,5,6,7,8,9]
    selector.setValue(3)
    assert selector.available() == [3]
    selector.clear_solve()
    assert selector.available() ==  [1,2,3,4,5,6,7,8,9]
    selector.setValue(3)
    selector.selected = True
    selector.clear_solve()
    assert selector.available() ==  [1,2,3,4,5,6,7,8,9]
