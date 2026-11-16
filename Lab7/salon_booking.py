import math

MAX_MINUTES = 24 * 60  # a single service can't last longer than a day
MAX_AMOUNT = 10_000_000  # sanity cap on a bill / discount amount


def _require_str(text, name):
    if not isinstance(text, str):
        raise ValueError(f"{name}: expected text input, got {type(text).__name__}")
    return text


def _to_finite_float(token, what):
    try:
        value = float(token)
    except (ValueError, OverflowError):
        raise ValueError(f"{what} must be a number, got {token.strip()!r}") from None
    if not math.isfinite(value):
        raise ValueError(f"{what} must be a finite number, got {token.strip()!r}")
    return value


def parse_booking(text):
    """'haircut:45' -> ('Haircut', 45.0). Raises ValueError on invalid input."""
    text = _require_str(text, "booking")
    parts = text.split(':')
    if len(parts) != 2:
        raise ValueError("booking must look like 'service:minutes' (exactly one ':')")
    service, minutes = parts[0].strip(), parts[1].strip()
    if not service:
        raise ValueError("service name must not be empty")
    minutes = _to_finite_float(minutes, "duration")
    if not 0 < minutes <= MAX_MINUTES:
        raise ValueError(f"duration must be between 0 and {MAX_MINUTES} minutes")
    return service.title(), minutes


def duration_average(durations_csv):
    """'30,45,60' -> 45 (integer average). Raises ValueError on invalid input."""
    text = _require_str(durations_csv, "durations")
    if not text.strip():
        raise ValueError("durations must not be empty")
    values = []
    for token in text.split(','):
        try:
            value = int(token)
        except ValueError:
            raise ValueError(f"duration must be a whole number, got {token.strip()!r}") from None
        if not 0 < value <= MAX_MINUTES:
            raise ValueError(f"each duration must be between 1 and {MAX_MINUTES} minutes, got {value}")
        values.append(value)
    return sum(values) // len(values)


def payable_bill(text):
    """'800|100' -> 844.0 (bill + 18% tax - discount, never below 0). Raises ValueError on invalid input."""
    text = _require_str(text, "bill")
    parts = text.split('|')
    if len(parts) != 2:
        raise ValueError("bill must look like 'amount|discount' (exactly one '|')")
    bill = _to_finite_float(parts[0], "bill amount")
    discount = _to_finite_float(parts[1], "discount")
    if bill < 0 or discount < 0:
        raise ValueError("bill amount and discount must not be negative")
    if bill > MAX_AMOUNT or discount > MAX_AMOUNT:
        raise ValueError(f"bill amount and discount must not exceed {MAX_AMOUNT}")
    total = bill * 1.18 - discount
    if not math.isfinite(total):
        raise ValueError("bill amount is too large")
    return max(total, 0)


def main():
    steps = [
        ("parse_booking", "Enter service:duration in min (e.g. haircut:45): ", parse_booking,
         "Service and Duration:"),
        ("duration_average", "Enter durations as CSV (e.g. 30,45,60): ", duration_average,
         "Average Duration:"),
        ("payable_bill", "Enter bill|discount (e.g. 800|100): ", payable_bill, "Payable Bill:"),
    ]
    for i, (name, prompt, func, label) in enumerate(steps):
        print(("\n" if i else "") + f"==== Running {name} ====")
        try:
            print(label, func(input(prompt)))
        except ValueError as e:
            print("Invalid input:", e)
        except EOFError:
            print("\nNo input received.")
            break


if __name__ == "__main__":
    main()
