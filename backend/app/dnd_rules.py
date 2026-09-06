from __future__ import annotations

from math import floor
import random

ABILITIES = {
    "strength": "СИЛА", "dexterity": "ЛОВКОСТЬ", "constitution": "ТЕЛОСЛОЖЕНИЕ",
    "intelligence": "ИНТЕЛЛЕКТ", "wisdom": "МУДРОСТЬ", "charisma": "ХАРИЗМА",
}
SKILLS = {
    "athletics": ("strength", "Атлетика"), "acrobatics": ("dexterity", "Акробатика"),
    "sleight_of_hand": ("dexterity", "Ловкость рук"), "stealth": ("dexterity", "Скрытность"),
    "arcana": ("intelligence", "Магия"), "history": ("intelligence", "История"),
    "investigation": ("intelligence", "Расследование"), "nature": ("intelligence", "Природа"),
    "religion": ("intelligence", "Религия"), "animal_handling": ("wisdom", "Уход за животными"),
    "insight": ("wisdom", "Проницательность"), "medicine": ("wisdom", "Медицина"),
    "perception": ("wisdom", "Внимательность"), "survival": ("wisdom", "Выживание"),
    "deception": ("charisma", "Обман"), "intimidation": ("charisma", "Запугивание"),
    "performance": ("charisma", "Выступление"), "persuasion": ("charisma", "Убеждение"),
}
CLASS_SKILLS = {
    "Воин": ["athletics", "intimidation"], "Плут": ["acrobatics", "stealth"],
    "Волшебник": ["arcana", "history"], "Жрец": ["insight", "religion"],
    "Следопыт": ["survival", "perception"], "Варвар": ["athletics", "survival"],
    "Бард": ["performance", "persuasion"], "Паладин": ["athletics", "persuasion"],
    "Колдун": ["arcana", "deception"],
}
CLASS_SAVES = {
    "Воин": ["strength", "constitution"], "Плут": ["dexterity", "intelligence"],
    "Волшебник": ["intelligence", "wisdom"], "Жрец": ["wisdom", "charisma"],
    "Следопыт": ["strength", "dexterity"], "Варвар": ["strength", "constitution"],
    "Бард": ["dexterity", "charisma"], "Паладин": ["wisdom", "charisma"],
    "Колдун": ["wisdom", "charisma"],
}
CLASS_HP = {"Воин":10,"Плут":8,"Волшебник":6,"Жрец":8,"Следопыт":10,"Варвар":12,"Бард":8,"Паладин":10,"Колдун":8}
WEAPONS = {
    "dagger": {"name":"Кинжал", "ability":"dexterity", "damage":4, "finesse":True},
    "shortsword": {"name":"Короткий меч", "ability":"dexterity", "damage":6, "finesse":True},
    "torch": {"name":"Факел", "ability":"strength", "damage":4, "finesse":False},
}
RACE_BONUSES = {
    "Человек": {k:1 for k in ABILITIES}, "Эльф":{"dexterity":2}, "Дварф":{"constitution":2},
    "Полурослик":{"dexterity":2}, "Полуорк":{"strength":2,"constitution":1}, "Гном":{"intelligence":2},
    "Тифлинг":{"charisma":2,"intelligence":1}, "Дроу":{"dexterity":2,"charisma":1},
}

def ability_modifier(score:int)->int: return floor((score-10)/2)
def proficiency_bonus(level:int)->int: return 2 + max(0,(level-1)//4)
def roll_d20()->int: return random.randint(1,20)
def roll_die(sides:int)->int: return random.randint(1,sides)

def d20_roll(modifier:int, target:int, proficiency:int=0, advantage:int=0, attack:bool=False):
    if advantage > 0: rolls=[roll_d20(),roll_d20()]; raw=max(rolls)
    elif advantage < 0: rolls=[roll_d20(),roll_d20()]; raw=min(rolls)
    else: rolls=[roll_d20()]; raw=rolls[0]
    total=raw+modifier+proficiency
    critical=attack and raw==20
    critical_failure=attack and raw==1
    success=critical or (not critical_failure and total>=target)
    return {"roll":raw,"rolls":rolls,"modifier":modifier,"proficiency":proficiency,"total":total,"target":target,"success":success,"critical":critical,"critical_failure":critical_failure,"advantage":advantage}

def character_derived(stats:dict[str,int], character_class:str, level:int=1)->dict:
    prof=proficiency_bonus(level); con=ability_modifier(stats.get("constitution",10)); dex=ability_modifier(stats.get("dexterity",10))
    class_skills=CLASS_SKILLS.get(character_class,[]); class_saves=CLASS_SAVES.get(character_class,[])
    return {"level":level,"proficiency_bonus":prof,"ability_modifiers":{k:ability_modifier(v) for k,v in stats.items()},
      "saving_throw_proficiencies":class_saves,"saving_throws":{k:ability_modifier(v)+(prof if k in class_saves else 0) for k,v in stats.items()},
      "skill_proficiencies":class_skills,"skills":{key:{"name":name,"ability":ability,"modifier":ability_modifier(stats.get(ability,10))+(prof if key in class_skills else 0),"proficient":key in class_skills} for key,(ability,name) in SKILLS.items()},
      "initiative":dex,"armor_class":10+dex,"max_hp":CLASS_HP.get(character_class,8)+con,"passive_perception":10+ability_modifier(stats.get("wisdom",10))+(prof if "perception" in class_skills else 0)}
