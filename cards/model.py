import xml.etree.ElementTree as ET
from typing import NamedTuple

from hearthstone.enums import CardClass, Race, CardType, CardSet, Rarity

from cards.fields import ParseField, BoolFromTag, IntFromTag, EnumFromTag, LocStringFromTag, FromAttrib


class CardMeta(type):
    def __new__(mcs, name, bases, nmspc):
        fields = [(name, field) for name, field in nmspc.items() if isinstance(field, ParseField)]

        type_ = NamedTuple(name, [(name, field.type) for name, field in fields])

        def from_entity(cls, entity: ET.Element):
            parsed = {}
            for field_name, field in fields:
                parsed[field_name] = field.parse_entity(entity)
            return cls(**parsed)

        type_.from_entity = classmethod(from_entity)
        return type_


class Card(metaclass=CardMeta):
    card_id = FromAttrib('CardID', str)
    id = FromAttrib('ID', int)
    name = LocStringFromTag('CARDNAME')
    inhand = LocStringFromTag('CARDTEXT_INHAND')

    health = IntFromTag('HEALTH')
    atk = IntFromTag('ATK')
    cost = IntFromTag('COST')

    collectable = BoolFromTag('COLLECTIBLE')

    card_class = EnumFromTag('CLASS', CardClass)
    race = EnumFromTag('CARDRACE', Race)
    type = EnumFromTag('CARDTYPE', CardType)
    card_set = EnumFromTag('CARD_SET', CardSet)
    rarity = EnumFromTag('RARITY', Rarity)

    @property
    def craftable(self):
        if isinstance(self.card_set, CardSet) and not self.card_set.craftable:
            return False
        if not self.type.craftable:
            return False
        if not self.rarity.craftable:
            return False
        return True

    @property
    def crafting_costs(self):
        if not self.craftable:
            return 0, 0
        return self.rarity.crafting_costs

    @property
    def disenchant_costs(self):
        if not self.craftable:
            return 0, 0
        return self.rarity.disenchant_costs

    @property
    def max_count_in_deck(self):
        if self.rarity == Rarity.LEGENDARY:
            return 1
        return 2


class Cards:
    pass