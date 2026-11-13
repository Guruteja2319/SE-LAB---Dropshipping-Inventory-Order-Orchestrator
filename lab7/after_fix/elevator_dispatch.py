"""Elevator dispatch input parsing functions hardened against invalid input."""


def parse_request(text):
    """Parse a request such as '5->9'; return None when input is invalid."""
    if not isinstance(text, str):
        return None

    parts = text.split("->")
    if len(parts) != 2:
        return None

    try:
        start = int(parts[0].strip())
        end = int(parts[1].strip())
    except (TypeError, ValueError):
        return None

    return start, end


def total_travel(floors_csv):
    """Return total movement between comma-separated floors, or None if invalid."""
    if not isinstance(floors_csv, str) or not floors_csv.strip():
        return None

    parts = floors_csv.split(",")
    if any(not part.strip() for part in parts):
        return None

    try:
        floors = [int(part.strip()) for part in parts]
    except (TypeError, ValueError):
        return None

    return sum(abs(floors[i + 1] - floors[i]) for i in range(len(floors) - 1))


def load_percent(text):
    """Calculate load percentage from 'X of Y'; return None for invalid input."""
    if not isinstance(text, str):
        return None

    parts = text.split(" of ")
    if len(parts) != 2:
        return None

    try:
        load = int(parts[0].strip())
        capacity = int(parts[1].strip())
    except (TypeError, ValueError):
        return None

    if load < 0 or capacity <= 0:
        return None

    return load * 100 // capacity


def main():
    print("==== Running parse_request ====")
    user_input = input("Enter a request as FROM->TO (e.g. 5->9): ")
    result = parse_request(user_input)
    print("From and To:", result if result is not None else "Invalid request")

    print("\n==== Running total_travel ====")
    user_input = input("Enter floors visited as CSV (e.g. 1,5,3,9): ")
    result = total_travel(user_input)
    print("Floors Travelled:", result if result is not None else "Invalid floor list")

    print("\n==== Running load_percent ====")
    user_input = input("Enter load as 'X of Y' (e.g. 450 of 630): ")
    result = load_percent(user_input)
    print("Load Percent:", result if result is not None else "Invalid load")


if __name__ == "__main__":
    main()
