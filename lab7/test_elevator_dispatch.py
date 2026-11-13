from hypothesis import given, strategies as st

from elevator_dispatch import parse_request, total_travel, load_percent


# Fuzz each function with arbitrary strings and None.
# The required property is that unexpected input must not crash the program.
arbitrary_input = st.one_of(st.text(), st.none())


@given(arbitrary_input)
def test_parse_request_no_crash(value):
    try:
        result = parse_request(value)
    except Exception as exc:
        assert False, f"parse_request crashed for {value!r}: {exc}"
    assert result is None or (
        isinstance(result, tuple)
        and len(result) == 2
        and all(isinstance(number, int) for number in result)
    )


@given(arbitrary_input)
def test_total_travel_no_crash(value):
    try:
        result = total_travel(value)
    except Exception as exc:
        assert False, f"total_travel crashed for {value!r}: {exc}"
    assert result is None or (isinstance(result, int) and result >= 0)


@given(arbitrary_input)
def test_load_percent_no_crash(value):
    try:
        result = load_percent(value)
    except Exception as exc:
        assert False, f"load_percent crashed for {value!r}: {exc}"
    assert result is None or (isinstance(result, int) and result >= 0)


# Check that valid generated inputs still produce correct results.
@given(st.integers(min_value=-10000, max_value=10000),
       st.integers(min_value=-10000, max_value=10000))
def test_parse_request_valid_values(start, end):
    assert parse_request(f"{start}->{end}") == (start, end)


@given(st.lists(st.integers(min_value=-1000, max_value=1000),
                min_size=1, max_size=30))
def test_total_travel_valid_values(floors):
    csv_value = ",".join(str(floor) for floor in floors)
    expected = sum(abs(floors[i + 1] - floors[i])
                   for i in range(len(floors) - 1))
    assert total_travel(csv_value) == expected


@given(st.integers(min_value=0, max_value=100000),
       st.integers(min_value=1, max_value=100000))
def test_load_percent_valid_values(load, capacity):
    assert load_percent(f"{load} of {capacity}") == load * 100 // capacity
