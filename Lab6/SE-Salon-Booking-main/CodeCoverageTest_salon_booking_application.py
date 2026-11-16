import pytest
from salon_booking import extra_time_charge, can_book, arrival_status


# ---------- Original tests ----------
def test_within_included_time():
    assert extra_time_charge("haircut", 20, "junior", False) == 0


def test_can_book():
    assert can_book(2, 1, False) is True


# ---------- extra_time_charge ----------
def test_unknown_service_raises():
    with pytest.raises(ValueError, match="unknown service"):
        extra_time_charge("massage", 30, "junior", False)


def test_negative_duration_raises():
    with pytest.raises(ValueError, match="invalid duration"):
        extra_time_charge("haircut", -1, "junior", False)


def test_exactly_included_time_is_free():
    assert extra_time_charge("colour", 60, "senior", False) == 0


def test_member_gets_15_extra_minutes_on_haircut():
    # included 30+15=45, extra 15, junior rate 10
    assert extra_time_charge("haircut", 60, "junior", True) == 150


def test_member_gets_no_bonus_on_spa():
    # included stays 90, extra 10, junior rate 10
    assert extra_time_charge("spa", 100, "junior", True) == 100


def test_non_member_haircut_junior_rate():
    # included 30, extra 20, rate 10
    assert extra_time_charge("haircut", 50, "junior", False) == 200


def test_non_junior_standard_rate():
    # included 30, extra 10, rate 18
    assert extra_time_charge("haircut", 40, "senior", False) == 180


def test_extra_exactly_60_has_no_surcharge():
    # extra 60 is not > 60, junior rate 10
    assert extra_time_charge("haircut", 90, "junior", False) == 600


def test_long_overrun_junior_surcharge():
    # extra 70, rate 10+8 = 18
    assert extra_time_charge("haircut", 100, "junior", False) == 1260


def test_long_overrun_senior_extra_surcharge():
    # extra 70, rate 18+8+4 = 30
    assert extra_time_charge("haircut", 100, "senior", False) == 2100


def test_long_overrun_other_level_no_senior_surcharge():
    # extra 70, rate 18+8 = 26
    assert extra_time_charge("haircut", 100, "mid", False) == 1820


# ---------- can_book ----------
def test_walk_in_party_of_two_ok():
    assert can_book(2, 5, True) is True


def test_walk_in_party_of_three_rejected():
    assert can_book(3, 1, True) is False


def test_booking_party_over_four_rejected():
    assert can_book(5, 1, False) is False


def test_booking_four_people_two_services_ok():
    assert can_book(4, 2, False) is True


def test_booking_too_many_services_rejected():
    assert can_book(4, 3, False) is False


# ---------- arrival_status ----------
def test_arrival_open_non_colour_weekday():
    assert arrival_status(5, False, False) == "open"


def test_arrival_late_non_colour_weekday():
    assert arrival_status(0, False, False) == "late"


def test_arrival_closed_non_colour_weekday():
    assert arrival_status(-11, False, False) == "closed"


def test_arrival_open_colour_weekday():
    assert arrival_status(10, True, False) == "open"


def test_arrival_late_colour_weekday():
    assert arrival_status(9, True, False) == "late"


def test_arrival_weekend_raises_cutoff():
    # non-colour weekend cutoff = 15
    assert arrival_status(10, False, True) == "late"
    assert arrival_status(15, False, True) == "open"


def test_arrival_colour_weekend_closed():
    # cutoff 20, late threshold 5
    assert arrival_status(4, True, True) == "closed"
