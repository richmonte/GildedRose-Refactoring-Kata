# -*- coding: utf-8 -*-

MAX_QUALITY = 50
MIN_QUALITY = 0

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
CONJURED_PREFIX = "Conjured"

CONJURED_DEGRADATION_RATE = 2


def increase_quality(item, amount=1):
    item.quality = min(MAX_QUALITY, item.quality + amount)


def decrease_quality(item, amount=1):
    item.quality = max(MIN_QUALITY, item.quality - amount)


class NormalItemUpdater:
    """Default behavior: quality degrades by 1/day, 2/day once past sell_in."""

    def update(self, item):
        decrease_quality(item)
        item.sell_in -= 1
        if item.sell_in < 0:
            decrease_quality(item)


class AgedBrieUpdater:
    """Quality improves with age, capped at MAX_QUALITY, doubling past sell_in."""

    def update(self, item):
        increase_quality(item)
        item.sell_in -= 1
        if item.sell_in < 0:
            increase_quality(item)


class SulfurasUpdater:
    """Legendary item: never sold, quality never changes."""

    def update(self, item):
        pass


class BackstagePassUpdater:
    """Quality rises as the concert approaches, then drops to zero after."""

    def update(self, item):
        increase_quality(item)
        if item.sell_in < 11:
            increase_quality(item)
        if item.sell_in < 6:
            increase_quality(item)
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = MIN_QUALITY


class ConjuredItemUpdater:
    """Degrades in quality twice as fast as a normal item."""

    def update(self, item):
        decrease_quality(item, CONJURED_DEGRADATION_RATE)
        item.sell_in -= 1
        if item.sell_in < 0:
            decrease_quality(item, CONJURED_DEGRADATION_RATE)


class GildedRose(object):

    _UPDATERS_BY_NAME = {
        AGED_BRIE: AgedBrieUpdater(),
        BACKSTAGE_PASSES: BackstagePassUpdater(),
        SULFURAS: SulfurasUpdater(),
    }
    _CONJURED_UPDATER = ConjuredItemUpdater()
    _DEFAULT_UPDATER = NormalItemUpdater()

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            self._select_updater(item).update(item)

    @classmethod
    def _select_updater(cls, item):
        if item.name in cls._UPDATERS_BY_NAME:
            return cls._UPDATERS_BY_NAME[item.name]
        if item.name.startswith(CONJURED_PREFIX):
            return cls._CONJURED_UPDATER
        return cls._DEFAULT_UPDATER


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
