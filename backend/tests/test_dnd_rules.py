import unittest
from unittest.mock import patch

from app.dnd_rules import ability_modifier, character_derived, proficiency_bonus, level_from_xp, d20_roll

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

    def test_real_xp_levels(self):
        self.assertEqual(level_from_xp(0), 1)
        self.assertEqual(level_from_xp(299), 1)
        self.assertEqual(level_from_xp(300), 2)
        self.assertEqual(level_from_xp(6400), 4)
        self.assertEqual(level_from_xp(355000), 20)

    def test_derived_sheet(self):
        stats={'strength':16,'dexterity':14,'constitution':15,'intelligence':10,'wisdom':12,'charisma':8}
        sheet=character_derived(stats,'Воин',1)
        self.assertEqual(sheet['proficiency_bonus'],2)
        self.assertEqual(sheet['ability_modifiers']['strength'],3)
        self.assertEqual(sheet['saving_throws']['strength'],5)
        self.assertEqual(sheet['initiative'],2)
        self.assertEqual(sheet['armor_class'],12)
        self.assertEqual(sheet['max_hp'],12)
        self.assertEqual(sheet['passive_perception'],11)

    @patch('app.dnd_rules.roll_d20', return_value=20)
    def test_attack_nat20_is_critical(self, _):
        result=d20_roll(3,30,2,attack=True)
        self.assertTrue(result['critical'])
        self.assertTrue(result['success'])

    @patch('app.dnd_rules.roll_d20', return_value=1)
    def test_attack_nat1_is_automatic_miss(self, _):
        result=d20_roll(20,1,6,attack=True)
        self.assertTrue(result['critical_failure'])
        self.assertFalse(result['success'])

    @patch('app.dnd_rules.roll_d20', return_value=1)
    def test_skill_nat1_is_not_automatic_failure(self, _):
        result=d20_roll(14,10,0,attack=False)
        self.assertTrue(result['success'])
        self.assertFalse(result['critical_failure'])

if __name__ == '__main__':
    unittest.main()
