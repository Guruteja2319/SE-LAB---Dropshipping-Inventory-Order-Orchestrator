def next_direction(current, direction, requests):
    above = [f for f in requests if f > current]
    below = [f for f in requests if f < current]
    if direction == "up":
        if above:
            return "up"
        if below:
            return "down"
        return "idle"
    if direction == "down":
        if below:
            return "down"
        if above:
            return "up"
        return "idle"
    if above:
        return "up"
    if below:
        return "down"
    return "idle"


def door_action(load_kg, blocked, emergency):
    if emergency:
        return "hold_open"
    if load_kg > 630:
        return "overload"
    if blocked:
        return "reopen"
    return "close"


def pick_elevator(cars, floor):
    best = None
    best_gap = None
    for name, position, is_idle in cars:
        gap = abs(position - floor)
        if not is_idle:
            gap += 5
        if best is None or gap < best_gap:
            best = name
            best_gap = gap
    return best
