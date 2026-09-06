import unittest

from app.dnd_rules import ability_modifier, character_derived, proficiency_bonus


class DndRulesTests(unittest.TestCase):
    def test_ability_modifiers(self):
        self.assertEqual(ability_modifier(8), -1)
        self.assertEqual(ability_modifier(10), 0)
        self.assertEqual(ability_modifier(18), 4)
        self.assertEqual(ability_modifier(20), 5)

    def test_proficiency_progression(self):
        self.assertEqual(proficiency_bonus(1), 2)
        self.assertEqual(proficiency_bonus(4), 2)
        self.assertEqual(proficiency_bonus(5), 3)
        self.assertEqual(proficiency_bonus(9), 4)

    def test_derived_sheet(self):
        stats = {
            'strength': 16,
            'dexterity': 14,
            'constitution': 15,
            'intelligence': 10,
            'wisdom': 12,
            'charisma': 8,
        }
        sheet = character_derived(stats, 'Воин', 1)
        self.assertEqual(sheet['proficiency_bonus'], 2)
        self.assertEqual(sheet['ability_modifiers']['strength'], 3)
        self.assertEqual(sheet['saving_throws']['strength'], 5)
        self.assertEqual(sheet['initiative'], 2)
        self.assertEqual(sheet['armor_class'], 12)
        self.assertEqual(sheet['max_hp'], 12)
        self.assertEqual(sheet['passive_perception'], 11)


if __name__ == '__main__':
    unittest.main()
