# -*- coding: utf-8 -*-

MAX_QUALITY = 50
MIN_QUALITY = 0

AGED_BRIE = "Aged Brie"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"


def increase_quality(item):
    if item.quality < MAX_QUALITY:
        item.quality += 1


def decrease_quality(item):
    if item.quality > MIN_QUALITY:
        item.quality -= 1


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


class GildedRose(object):

    _UPDATERS_BY_NAME = {
        AGED_BRIE: AgedBrieUpdater(),
        BACKSTAGE_PASSES: BackstagePassUpdater(),
        SULFURAS: SulfurasUpdater(),
    }
    _DEFAULT_UPDATER = NormalItemUpdater()

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            updater = self._UPDATERS_BY_NAME.get(item.name, self._DEFAULT_UPDATER)
            updater.update(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
