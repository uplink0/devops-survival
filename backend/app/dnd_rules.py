from __future__ import annotations

from dataclasses import dataclass
from math import floor
import random

ABILITIES = {
    "strength": "СИЛА",
    "dexterity": "ЛОВКОСТЬ",
    "constitution": "ТЕЛОСЛОЖЕНИЕ",
    "intelligence": "ИНТЕЛЛЕКТ",
    "wisdom": "МУДРОСТЬ",
    "charisma": "ХАРИЗМА",
}

SKILLS = {
    "athletics": ("strength", "Атлетика"),
    "acrobatics": ("dexterity", "Акробатика"),
    "sleight_of_hand": ("dexterity", "Ловкость рук"),
    "stealth": ("dexterity", "Скрытность"),
    "arcana": ("intelligence", "Магия"),
    "history": ("intelligence", "История"),
    "investigation": ("intelligence", "Расследование"),
    "nature": ("intelligence", "Природа"),
    "religion": ("intelligence", "Религия"),
    "animal_handling": ("wisdom", "Уход за животными"),
    "insight": ("wisdom", "Проницательность"),
    "medicine": ("wisdom", "Медицина"),
    "perception": ("wisdom", "Внимательность"),
    "survival": ("wisdom", "Выживание"),
    "deception": ("charisma", "Обман"),
    "intimidation": ("charisma", "Запугивание"),
    "performance": ("charisma", "Выступление"),
    "persuasion": ("charisma", "Убеждение"),
}

CLASS_SKILLS = {
    "Воин": ["athletics", "intimidation"],
    "Плут": ["acrobatics", "stealth", "sleight_of_hand", "investigation"],
    "Волшебник": ["arcana", "history"],
    "Жрец": ["insight", "religion"],
    "Следопыт": ["survival", "perception"],
    "Варвар": ["athletics", "survival"],
    "Бард": ["performance", "persuasion"],
    "Паладин": ["athletics", "persuasion"],
    "Колдун": ["arcana", "deception"],
}

CLASS_SAVES = {
    "Воин": ["strength", "constitution"],
    "Плут": ["dexterity", "intelligence"],
    "Волшебник": ["intelligence", "wisdom"],
    "Жрец": ["wisdom", "charisma"],
    "Следопыт": ["strength", "dexterity"],
    "Варвар": ["strength", "constitution"],
    "Бард": ["dexterity", "charisma"],
    "Паладин": ["wisdom", "charisma"],
    "Колдун": ["wisdom", "charisma"],
}

CLASS_HP = {
    "Воин": 10,
    "Плут": 8,
    "Волшебник": 6,
    "Жрец": 8,
    "Следопыт": 10,
    "Варвар": 12,
    "Бард": 8,
    "Паладин": 10,
    "Колдун": 8,
}

RACE_BONUSES = {
    "Человек": {k: 1 for k in ABILITIES},
    "Эльф": {"dexterity": 2},
    "Дварф": {"constitution": 2},
    "Полурослик": {"dexterity": 2},
    "Полуорк": {"strength": 2, "constitution": 1},
    "Гном": {"intelligence": 2},
    "Тифлинг": {"charisma": 2, "intelligence": 1},
    "Дроу": {"dexterity": 2, "charisma": 1},
}


def ability_modifier(score: int) -> int:
    return floor((score - 10) / 2)


def proficiency_bonus(level: int) -> int:
    return 2 + max(0, (level - 1) // 4)


def roll_d20() -> int:
    return random.randint(1, 20)


@dataclass(frozen=True)
class CheckResult:
    roll: int
    modifier: int
    proficiency: int
    total: int
    dc: int
    success: bool
    critical: bool
    critical_failure: bool


def ability_check(score: int, dc: int, proficient: bool = False, level: int = 1, advantage: int = 0) -> CheckResult:
    if advantage > 0:
        roll = max(roll_d20(), roll_d20())
    elif advantage < 0:
        roll = min(roll_d20(), roll_d20())
    else:
        roll = roll_d20()
    mod = ability_modifier(score)
    prof = proficiency_bonus(level) if proficient else 0
    total = roll + mod + prof
    return CheckResult(roll, mod, prof, total, dc, total >= dc, roll == 20, roll == 1)


def character_derived(stats: dict[str, int], character_class: str, level: int = 1) -> dict:
    prof = proficiency_bonus(level)
    con_mod = ability_modifier(stats.get("constitution", 10))
    dex_mod = ability_modifier(stats.get("dexterity", 10))
    return {
        "level": level,
        "proficiency_bonus": prof,
        "ability_modifiers": {k: ability_modifier(v) for k, v in stats.items()},
        "saving_throw_proficiencies": CLASS_SAVES.get(character_class, []),
        "saving_throws": {
            k: ability_modifier(v) + (prof if k in CLASS_SAVES.get(character_class, []) else 0)
            for k, v in stats.items()
        },
        "skill_proficiencies": CLASS_SKILLS.get(character_class, []),
        "skills": {
            key: {
                "name": name,
                "ability": ability,
                "modifier": ability_modifier(stats.get(ability, 10)) + (prof if key in CLASS_SKILLS.get(character_class, []) else 0),
                "proficient": key in CLASS_SKILLS.get(character_class, []),
            }
            for key, (ability, name) in SKILLS.items()
        },
        "initiative": dex_mod,
        "armor_class": 10 + dex_mod,
        "max_hp": CLASS_HP.get(character_class, 8) + con_mod,
        "passive_perception": 10 + ability_modifier(stats.get("wisdom", 10)) + (prof if "perception" in CLASS_SKILLS.get(character_class, []) else 0),
    }
