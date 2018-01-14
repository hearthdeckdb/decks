from abc import ABC, abstractmethod
from enum import EnumMeta
from typing import Callable, Any, Optional
from xml.etree import ElementTree as ET


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