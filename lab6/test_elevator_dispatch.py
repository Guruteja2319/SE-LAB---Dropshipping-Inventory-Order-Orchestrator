import pytest
from elevator_dispatch import next_direction, door_action, pick_elevator

#Example test cases:
def test_emergency_holds_doors():
    assert door_action(100, False, True) == "hold_open"

def test_idle_with_no_requests():
    assert next_direction(3, "idle", []) == "idle"

#Write the rest of the test cases so that the code is 90- 100% covered.
