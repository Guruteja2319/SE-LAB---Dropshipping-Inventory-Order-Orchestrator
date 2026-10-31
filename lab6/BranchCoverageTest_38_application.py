from elevator_dispatch import next_direction, door_action, pick_elevator


def test_next_direction_all_branches():
    # direction == "up"
    assert next_direction(3, "up", [5]) == "up"
    assert next_direction(3, "up", [1]) == "down"
    assert next_direction(3, "up", []) == "idle"

    # direction == "down"
    assert next_direction(5, "down", [2]) == "down"
    assert next_direction(5, "down", [8]) == "up"
    assert next_direction(5, "down", []) == "idle"

    # idle/other direction
    assert next_direction(3, "idle", [6]) == "up"
    assert next_direction(5, "idle", [2]) == "down"
    assert next_direction(3, "idle", []) == "idle"


def test_door_action_all_branches():
    assert door_action(100, False, True) == "hold_open"
    assert door_action(700, False, False) == "overload"
    assert door_action(100, True, False) == "reopen"
    assert door_action(100, False, False) == "close"


def test_pick_elevator_branches():
    cars = [
        ("E1", 2, True),
        ("E2", 8, False),
        ("E3", 4, True)
    ]
    assert pick_elevator(cars, 3) == "E1"

    cars = [
        ("E1", 4, False),
        ("E2", 8, True)
    ]
    assert pick_elevator(cars, 5) == "E2"

    assert pick_elevator([], 5) is None