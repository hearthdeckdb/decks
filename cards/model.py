import os
import xml.etree.ElementTree as ET
from typing import NamedTuple, Dict, Tuple, Any, Union

from hearthstone.enums import CardClass, Race, CardType, CardSet, Rarity

import config
from cards.fields import ParseField, BoolFromTag, IntFromTag, EnumFromTag, LocStringFromTag, FromAttrib


class CardMeta(type):
    def __new__(mcs, name, bases, nmspc):
        fields = [(name, field) for name, field in nmspc.items() if isinstance(field, ParseField)]
        not_fields = [(name, attrib) for name, attrib in nmspc.items() if not isinstance(attrib, ParseField)]
        type_ = NamedTuple(name, [(name, field.type) for name, field in fields])

        def from_entity(cls, entity: ET.Element):
            parsed = {}
            for field_name, field in fields:
                parsed[field_name] = field.parse_entity(entity)
            return cls(**parsed)

        type_.from_entity = classmethod(from_entity)
        for name, atrib in not_fields:
            setattr(type_, name, atrib)

        type_.field_names = [name for name, _ in fields]
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

    def raw_value(self, name: str) -> Union[int, bool, str]:
        value = getattr(self, name)
        if hasattr(value, 'value'):
            return value.value
        return value

    @property
    def dict(self) -> Dict[str, Any]:
        dict = {name: self.raw_value(name) for name in self.field_names}
        for calculated in ['craftable', 'crafting_costs', 'disenchant_costs', 'max_count_in_deck']:
            dict[calculated] = getattr(self, calculated)
        return dict

    @property
    def craftable(self) -> bool:
        if isinstance(self.card_set, CardSet) and not self.card_set.craftable:
            return False
        if not self.type.craftable:
            return False
        if not self.rarity.craftable:
            return False
        return True

    @property
    def crafting_costs(self) -> Tuple[int, int]:
        if not self.craftable:
            return 0, 0
        return self.rarity.crafting_costs

    @property
    def disenchant_costs(self) -> Tuple[int, int]:
        if not self.craftable:
            return 0, 0
        return self.rarity.disenchant_costs

    @property
    def max_count_in_deck(self) -> int:
        if self.rarity == Rarity.LEGENDARY:
            return 1
        return 2


class Cards:
    @classmethod
    def get_card_defs_contents(cls):
        with open(os.path.join(config.ASSETS_PATH, 'CardDefs.xml')) as f:
            return f.read()

    @classmethod
    def all_cards(cls) -> Dict[int, Card]:
        if not hasattr(cls, '_cards'):
            xml = ET.fromstring(cls.get_card_defs_contents())
            assert xml.tag == 'CardDefs'
            cls._cards = {card.id: card for card in map(Card.from_entity, xml)}
        return cls._cards
