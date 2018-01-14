import xml.etree.ElementTree as ET

import pytest
from hearthstone.enums import CardClass, Race, CardType, Rarity, CardSet

from cards.model import Card, BoolFromTag, FromTag, FromAttrib

empty_card = ET.fromstring('''<Entity CardID="" ID="0"/>''')

example_card = ET.fromstring('''<Entity CardID="CARD_ID" ID="42" version="2">
    <Tag enumID="185" name="CARDNAME" type="LocString">
        <deDE>Schrumpfstrahl</deDE>
        <enUS>Shrink Ray</enUS>
        <esES>Rayo reductor</esES>
        <esMX>Rayo reductor</esMX>
        <frFR>Rayon réducteur</frFR>
        <itIT>Raggio Riduttore</itIT>
        <jaJP>縮小光線</jaJP>
        <koKR>축소 광선</koKR>
        <plPL>Promień skurczający</plPL>
        <ptBR>Raio Encolhedor</ptBR>
        <ruRU>Уменьшающий луч</ruRU>
        <thTH>ลำแสงย่อส่วน</thTH>
        <zhCN>缩小射线</zhCN>
        <zhTW>縮小射線</zhTW>
    </Tag>
    
    <Tag enumID="184" name="CARDTEXT_INHAND" type="LocString">
        <deDE>-2 Angriff in diesem Zug.</deDE>
        <enUS>-2 Attack this turn.</enUS>
        <esES>-2 p. de ataque este turno.</esES>
        <esMX>-2 de Ataque en este turno.</esMX>
        <frFR>-2 ATQ pendant ce tour.</frFR>
        <itIT>-2 Attacco per questo turno.</itIT>
        <jaJP>このターンの間、攻撃力-2。</jaJP>
        <koKR>이번 턴에 공격력 -2</koKR>
        <plPL>-2 do ataku w tej turze.</plPL>
        <ptBR>-2 de Ataque neste turno.</ptBR>
        <ruRU>-2 к атаке до конца хода.</ruRU>
        <thTH>พลังโจมตี -2 ในเทิร์นนี้</thTH>
        <zhCN>在本回合中，获得-2攻击力。</zhCN>
        <zhTW>本回合-2攻擊力</zhTW>
    </Tag>
    
    <Tag enumID="45" name="HEALTH" type="Int" value="1"/>
    <Tag enumID="47" name="ATK" type="Int" value="2"/>
    <Tag enumID="48" name="COST" type="Int" value="3"/>
    <Tag enumID="183" name="CARD_SET" type="Int" value="13"/>
    <Tag enumID="199" name="CLASS" type="Int" value="12"/>
    <Tag enumID="200" name="CARDRACE" type="Int" value="17"/>
    <Tag enumID="202" name="CARDTYPE" type="Int" value="4"/>
    <Tag enumID="203" name="RARITY" type="Int" value="1"/>
    <Tag enumID="321" name="COLLECTIBLE" type="Int" value="1"/>
</Entity>
''')

attrib_test_data = [
    ('card_id', 'CARD_ID'),
    ('id', 42),
    ('health', 1),
    ('atk', 2),
    ('cost', 3),
    ('collectable', True),
    ('card_class', CardClass.NEUTRAL),
    ('race', Race.MECHANICAL),
    ('type', CardType.MINION),
    ('rarity', Rarity.COMMON),
    ('card_set', CardSet.GVG),
    ('name', 'Shrink Ray'),
    ('inhand', '-2 Attack this turn.')
]


def test_from_attrib_parse_attrib():
    fa = FromAttrib('the_attrib', int)
    assert fa.parse_entity(ET.fromstring('<Entity the_attrib="42"></Entity>')) == 42


def test_from_tag_parse_tag():
    ft = FromTag('the_tag', int)
    assert ft.parse_entity(ET.fromstring('<Entity><Tag name="the_tag" value="43" /></Entity>')) == 43


def test_from_tag_set_none_if_tag_do_not_exists():
    card = Card.from_entity(empty_card)
    assert card.health is None


def test_from_tag_bool_set_false_if_tag_do_not_exists():
    b = BoolFromTag('the_bool_tag')
    assert b.parse_entity(ET.fromstring('<Entity><Tag name="other_tag" value="1" /></Entity>')) is False


def test_from_tag_bool_set_true_if_tag_value_is_1():
    b = BoolFromTag('the_bool_tag')
    assert b.parse_entity(ET.fromstring('<Entity><Tag name="the_bool_tag" value="1" /></Entity>')) is True


@pytest.mark.parametrize("name,expected", attrib_test_data)
def test_card_has_correct_attrib(name, expected):
    card = Card.from_entity(example_card)
    assert getattr(card, name) == expected
