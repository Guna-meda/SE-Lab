import math

from hypothesis import given, settings, strategies as st

from salon_booking import parse_booking, duration_average, payable_bill

# Inputs of every flavour: arbitrary text, None, numbers, lists, bytes ...
anything = st.text() | st.none() | st.integers() | st.floats() | st.binary() | st.lists(st.integers())


# ---------------------------------------------------------------------------
# 1. "No crash" fuzz tests.
#    A function may reject bad input, but only with a clean ValueError.
#    Any other exception (TypeError, AttributeError, ZeroDivisionError,
#    OverflowError ...) is a bug.
# ---------------------------------------------------------------------------
@given(anything)
def test_parse_booking_no_crash(s):
    try:
        parse_booking(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"parse_booking crashed with: {type(e).__name__}: {e}"


@given(anything)
def test_duration_average_no_crash(s):
    try:
        duration_average(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"duration_average crashed with: {type(e).__name__}: {e}"


@given(anything)
def test_payable_bill_no_crash(s):
    try:
        payable_bill(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"payable_bill crashed with: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# 2. Property tests on *valid-looking* input: the result must be sensible.
# ---------------------------------------------------------------------------
service_names = st.text(alphabet=st.characters(blacklist_characters=":", blacklist_categories=("Cs", "Cc")),
                        min_size=1).filter(lambda t: t.strip() != "")


@given(service_names, st.floats(min_value=0.01, max_value=1440, allow_nan=False))
def test_parse_booking_valid_roundtrip(name, minutes):
    service, mins = parse_booking(f"{name}:{minutes}")
    assert service == service.strip() and service != ""
    assert math.isfinite(mins) and mins > 0


@given(st.lists(st.integers(min_value=1, max_value=1440), min_size=1, max_size=50))
def test_duration_average_between_min_and_max(values):
    avg = duration_average(",".join(map(str, values)))
    assert min(values) <= avg <= max(values)


@given(st.floats(min_value=0, max_value=1e6, allow_nan=False),
       st.floats(min_value=0, max_value=1e6, allow_nan=False))
def test_payable_bill_never_negative_and_finite(bill, discount):
    result = payable_bill(f"{bill}|{discount}")
    assert math.isfinite(result) and result >= 0


# ---------------------------------------------------------------------------
# 3. Explicit regression cases for edge cases the fuzzer discovered.
# ---------------------------------------------------------------------------
import pytest


@pytest.mark.parametrize("bad", [None, "", "haircut", "haircut:", ":45", "a:b:c", "cut:abc",
                                 "cut:nan", "cut:inf", "cut:-5", "cut:0", "   :30", 42])
def test_parse_booking_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        parse_booking(bad)


@pytest.mark.parametrize("bad", [None, "", "1,,3", "one,two", "1,2,", ",", "0", "-5,10", "1.5,2", 7])
def test_duration_average_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        duration_average(bad)


@pytest.mark.parametrize("bad", [None, "", "800", "800|", "|100", "a|b", "1|2|3",
                                 "nan|0", "inf|0", "100|nan", "-100|0", "100|-5", "1e308|0", 5])
def test_payable_bill_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        payable_bill(bad)


def test_known_good_values():
    assert parse_booking(" haircut : 45 ") == ("Haircut", 45.0)
    assert duration_average("30,45,60") == 45
    assert payable_bill("800|100") == pytest.approx(844.0)
    assert payable_bill("100|500") == 0
