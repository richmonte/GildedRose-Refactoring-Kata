# -*- coding: utf-8 -*-
import pytest

from gilded_rose import GildedRose, Item

NORMAL_ITEM = "+5 Dexterity Vest"
AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
CONJURED_ITEM = "Conjured Mana Cake"


def update_quality(item):
    """Run a single update_quality() tick on one Item and return it."""
    GildedRose([item]).update_quality()
    return item


# ---------------------------------------------------------------------------
# Normal items
# ---------------------------------------------------------------------------

def test_normal_item_quality_decreases_by_one_before_sell_by_date():
    item = update_quality(Item(NORMAL_ITEM, sell_in=10, quality=20))
    assert item.quality == 19
    assert item.sell_in == 9


def test_normal_item_quality_decreases_by_two_once_past_sell_by_date():
    item = update_quality(Item(NORMAL_ITEM, sell_in=-1, quality=10))
    assert item.quality == 8


def test_normal_item_quality_stays_at_zero_floor():
    item = update_quality(Item(NORMAL_ITEM, sell_in=5, quality=0))
    assert item.quality == 0


def test_normal_item_quality_does_not_go_negative_when_sell_in_hits_zero():
    # sell_in crosses from 0 to -1 within this same call, so both the
    # "before sell date" decrement and the "past sell date" decrement are
    # attempted in one update_quality() invocation. quality must floor at 0
    # rather than the two decrements taking it to -1.
    item = update_quality(Item(NORMAL_ITEM, sell_in=0, quality=1))
    assert item.quality == 0
    assert item.sell_in == -1


def test_normal_item_quality_does_not_go_negative_when_already_past_date():
    item = update_quality(Item(NORMAL_ITEM, sell_in=-5, quality=1))
    assert item.quality == 0


@pytest.mark.parametrize("starting_sell_in", [5, 0, -3])
def test_normal_item_sell_in_decreases_by_one_each_day(starting_sell_in):
    item = update_quality(Item(NORMAL_ITEM, sell_in=starting_sell_in, quality=10))
    assert item.sell_in == starting_sell_in - 1


# ---------------------------------------------------------------------------
# Aged Brie
# ---------------------------------------------------------------------------

def test_aged_brie_quality_increases_by_one_before_sell_by_date():
    item = update_quality(Item(AGED_BRIE, sell_in=5, quality=10))
    assert item.quality == 11
    assert item.sell_in == 4


def test_aged_brie_quality_increases_by_two_once_past_sell_by_date():
    item = update_quality(Item(AGED_BRIE, sell_in=-3, quality=10))
    assert item.quality == 12


def test_aged_brie_quality_does_not_exceed_fifty_before_sell_by_date():
    item = update_quality(Item(AGED_BRIE, sell_in=5, quality=50))
    assert item.quality == 50


@pytest.mark.parametrize(
    "starting_quality",
    [
        50,  # already at the cap: must stay at 50
        49,  # one below the cap: must land exactly on 50, not 51
    ],
)
def test_aged_brie_quality_does_not_exceed_fifty_at_sell_in_zero(starting_quality):
    # At sell_in=0, Aged Brie gets two increment attempts in the same call:
    # the normal "ages well" +1, and a second +1 once sell_in has ticked
    # past 0 to -1. Both are guarded by `quality < 50`, so the cap must
    # hold even when the two attempts land back-to-back.
    item = update_quality(Item(AGED_BRIE, sell_in=0, quality=starting_quality))
    assert item.quality == 50


def test_aged_brie_quality_does_not_exceed_fifty_when_already_past_date():
    item = update_quality(Item(AGED_BRIE, sell_in=-1, quality=49))
    assert item.quality == 50


# ---------------------------------------------------------------------------
# Sulfuras
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sell_in, quality",
    [
        (0, 80),
        (-1, 80),
        (5, 80),
        (-1, 79),   # holds regardless of starting quality, not just 80
        (-1, 0),
    ],
)
def test_sulfuras_never_changes(sell_in, quality):
    item = update_quality(Item(SULFURAS, sell_in=sell_in, quality=quality))
    assert item.quality == quality
    assert item.sell_in == sell_in


# ---------------------------------------------------------------------------
# Backstage passes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sell_in, expected_quality",
    [
        (11, 21),  # just outside the "10 days or less" window: +1 only
        (10, 22),  # boundary: "10 days or less" window: +2
        (6, 22),   # just outside the "5 days or less" window: still +2
        (5, 23),   # boundary: "5 days or less" window: +3
    ],
)
def test_backstage_passes_quality_increase_by_sell_in_window(sell_in, expected_quality):
    item = update_quality(Item(BACKSTAGE_PASSES, sell_in=sell_in, quality=20))
    assert item.quality == expected_quality
    assert item.sell_in == sell_in - 1


def test_backstage_passes_quality_drops_to_zero_after_the_concert():
    item = update_quality(Item(BACKSTAGE_PASSES, sell_in=0, quality=20))
    assert item.quality == 0
    assert item.sell_in == -1


def test_backstage_passes_quality_does_not_exceed_fifty_at_sell_in_15():
    # sell_in=15 is outside both the "10 days or less" and "5 days or
    # less" windows, so only the base +1 is attempted. Starting already
    # at the cap confirms that single increment is still blocked.
    item = update_quality(Item(BACKSTAGE_PASSES, sell_in=15, quality=50))
    assert item.quality == 50


def test_backstage_passes_quality_does_not_exceed_fifty_at_sell_in_10():
    # sell_in=10 is within the "10 days or less" window, so two increment
    # attempts (+1, then +1 more) happen in this one call. Starting one
    # below the cap confirms the second attempt is blocked rather than
    # overshooting to 51.
    item = update_quality(Item(BACKSTAGE_PASSES, sell_in=10, quality=49))
    assert item.quality == 50


def test_backstage_passes_quality_does_not_exceed_fifty_with_triple_bump():
    # sell_in=5 is within both bonus windows, so three increment attempts
    # (+1, +1, +1) happen in this one call. Starting two below the cap
    # confirms the third attempt is blocked rather than overshooting to 51.
    item = update_quality(Item(BACKSTAGE_PASSES, sell_in=5, quality=48))
    assert item.quality == 50


# ---------------------------------------------------------------------------
# Conjured items
#
# The requirements say Conjured items should degrade in quality twice as
# fast as normal items, but update_quality() has no special case for them
# at all -- they fall through to the normal-item branch. These tests
# characterize that *current* (spec-violating) behavior as a golden master,
# so that fixing it later shows up as a deliberate, visible diff to these
# tests rather than an accidental behavior change during refactoring.
# ---------------------------------------------------------------------------

def test_conjured_item_currently_degrades_at_normal_rate_before_sell_by_date():
    item = update_quality(Item(CONJURED_ITEM, sell_in=3, quality=6))
    assert item.quality == 5  # spec would require 4
    assert item.sell_in == 2


def test_conjured_item_currently_degrades_at_normal_rate_past_sell_by_date():
    item = update_quality(Item(CONJURED_ITEM, sell_in=-1, quality=6))
    assert item.quality == 4  # spec would require 2


# ---------------------------------------------------------------------------
# Cross-cutting
# ---------------------------------------------------------------------------

def test_update_quality_handles_a_mixed_list_of_items_independently():
    items = [
        Item(NORMAL_ITEM, sell_in=10, quality=20),
        Item(AGED_BRIE, sell_in=2, quality=0),
        Item(SULFURAS, sell_in=0, quality=80),
        Item(BACKSTAGE_PASSES, sell_in=15, quality=20),
        Item(CONJURED_ITEM, sell_in=3, quality=6),
    ]

    GildedRose(items).update_quality()

    normal, brie, sulfuras, backstage, conjured = items
    assert (normal.quality, normal.sell_in) == (19, 9)
    assert (brie.quality, brie.sell_in) == (1, 1)
    assert (sulfuras.quality, sulfuras.sell_in) == (80, 0)
    assert (backstage.quality, backstage.sell_in) == (21, 14)
    assert (conjured.quality, conjured.sell_in) == (5, 2)
