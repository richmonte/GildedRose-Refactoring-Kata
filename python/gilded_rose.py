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


class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name == SULFURAS:
                # Legendary item: never sold, quality never changes.
                continue

            if item.name in (AGED_BRIE, BACKSTAGE_PASSES):
                increase_quality(item)
                if item.name == BACKSTAGE_PASSES:
                    if item.sell_in < 11:
                        increase_quality(item)
                    if item.sell_in < 6:
                        increase_quality(item)
            else:
                decrease_quality(item)

            item.sell_in -= 1

            if item.sell_in < 0:
                if item.name == AGED_BRIE:
                    increase_quality(item)
                elif item.name == BACKSTAGE_PASSES:
                    item.quality = MIN_QUALITY
                else:
                    decrease_quality(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
