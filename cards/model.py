import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from enum import EnumMeta
from typing import NamedTuple, Any, Optional, Callable

from hearthstone.enums import CardClass, Race, CardType, CardSet, Rarity


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


class ParseField(ABC):
    def __init__(self, name: str, type_: type, factory: Callable = None):
        self.name = name
        self.type = type_
        if factory is None:
            factory = type_
        self.factory = factory

    @abstractmethod
    def get_value(self, entity: ET.Element) -> Any:
        pass

    def parse_entity(self, entity: ET.Element) -> Optional[Any]:
        assert entity.tag == 'Entity'
        result = self.get_value(entity)
        if result is not None:
            return self.factory(result)
        return None


class FromTag(ParseField):
    def get_value(self, entity: ET.Element):
        for tag in entity:
            if tag.tag == 'Tag' and tag.attrib['name'] == self.name:
                return tag.attrib['value']


class BoolFromTag(FromTag):
    def __init__(self, name: str):
        super().__init__(name, int, bool)

    def get_value(self, entity: ET.Element):
        return super().get_value(entity) == '1'


class IntFromTag(FromTag):
    def __init__(self, name: str):
        super().__init__(name, int)


class EnumFromTag(FromTag):
    def __init__(self, name: str, enum: EnumMeta):
        super().__init__(name, enum, lambda value: enum(int(value)))


class LocStringFromTag(FromTag):
    lang = 'enUS'

    def __init__(self, name: str):
        super().__init__(name, str)

    def get_value(self, entity: ET.Element):
        for tag in entity:
            if tag.tag == 'Tag' and tag.attrib['name'] == self.name:
                for lang_tag in tag:
                    if lang_tag.tag == self.lang:
                        return lang_tag.text


class FromAttrib(ParseField):
    def get_value(self, entity: ET.Element):
        return entity.attrib[self.name]


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
