from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..auth import current_user
from ..db import get_db
from ..dnd_rules import ABILITIES, SKILLS, WEAPONS, CLASS_SAVES, ability_modifier, character_derived, d20_roll, proficiency_bonus, roll_die
from ..models import User, InventoryItem

router = APIRouter(prefix='/api', tags=['rules'])


def stats_for(user: User):
    return {k: getattr(user, k) or 10 for k in ABILITIES}


def level_for(user: User):
    return max(1, (user.xp // 250) + 1)


class RollIn(BaseModel):
    kind: str = Field(min_length=3, max_length=16)  # skill | save | attack | damage
    key: str = Field(min_length=1, max_length=64)
    target: int = Field(default=15, ge=1, le=30)
    advantage: int = Field(default=0, ge=-1, le=1)


@router.get('/character/sheet')
def character_sheet(user: User = Depends(current_user)):
    if not user.character_name:
        raise HTTPException(404, 'Персонаж не создан')
    stats = stats_for(user)
    return {
        'character': {'name': user.character_name, 'race': user.character_race, 'class': user.character_class,
                      'background': user.character_background, 'stats': stats},
        'derived': character_derived(stats, user.character_class or '', level_for(user)),
    }


@router.post('/dnd/roll')
def dnd_roll(data: RollIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not user.character_name:
        raise HTTPException(400, 'Сначала создай персонажа')
    stats = stats_for(user)
    level = level_for(user)
    prof = proficiency_bonus(level)
    derived = character_derived(stats, user.character_class or '', level)

    if data.kind == 'skill':
        skill = SKILLS.get(data.key)
        if not skill:
            raise HTTPException(404, 'Навык не найден')
        ability, name = skill
        proficient = data.key in derived['skill_proficiencies']
        result = d20_roll(ability_modifier(stats[ability]), data.target, prof if proficient else 0, data.advantage)
        return {'kind':'skill','key':data.key,'name':name,'ability':ability,**result}

    if data.kind == 'save':
        ability = data.key if data.key in ABILITIES else None
        if not ability:
            raise HTTPException(404, 'Характеристика для спасброска не найдена')
        proficient = ability in derived['saving_throw_proficiencies']
        result = d20_roll(ability_modifier(stats[ability]), data.target, prof if proficient else 0, data.advantage)
        return {'kind':'save','key':ability,'name':ABILITIES[ability],**result}

    if data.kind == 'attack':
        weapon = WEAPONS.get(data.key)
        if not weapon:
            raise HTTPException(404, 'Оружие не поддерживается')
        owned = db.query(InventoryItem).filter(InventoryItem.user_id == user.id, InventoryItem.item_key == data.key, InventoryItem.quantity > 0).first()
        if not owned:
            raise HTTPException(400, 'Оружие отсутствует в инвентаре')
        ability = weapon['ability']
        if weapon.get('finesse'):
            ability = 'dexterity' if stats['dexterity'] >= stats['strength'] else 'strength'
        result = d20_roll(ability_modifier(stats[ability]), data.target, prof, data.advantage, attack=True)
        return {'kind':'attack','key':data.key,'name':weapon['name'],'ability':ability,'damage_die':weapon['damage'],**result}

    if data.kind == 'damage':
        weapon = WEAPONS.get(data.key)
        if not weapon:
            raise HTTPException(404, 'Оружие не поддерживается')
        owned = db.query(InventoryItem).filter(InventoryItem.user_id == user.id, InventoryItem.item_key == data.key, InventoryItem.quantity > 0).first()
        if not owned:
            raise HTTPException(400, 'Оружие отсутствует в инвентаре')
        ability = weapon['ability']
        if weapon.get('finesse'):
            ability = 'dexterity' if stats['dexterity'] >= stats['strength'] else 'strength'
        critical = data.target == 20
        raw = roll_die(weapon['damage']) + (roll_die(weapon['damage']) if critical else 0)
        total = raw + ability_modifier(stats[ability])
        return {'kind':'damage','key':data.key,'name':weapon['name'],'damage_die':weapon['damage'],'roll':raw,'ability_modifier':ability_modifier(stats[ability]),'total':max(1,total),'critical':critical}

    raise HTTPException(400, 'Неизвестный тип броска')


# Backward-compatible endpoint used by the current sidebar.
class CheckIn(BaseModel):
    skill: str = Field(min_length=1, max_length=64)
    dc: int = Field(ge=1, le=30)
    advantage: int = Field(default=0, ge=-1, le=1)


@router.post('/check')
def make_check(data: CheckIn, user: User = Depends(current_user)):
    result = dnd_roll(RollIn(kind='skill', key=data.skill, target=data.dc, advantage=data.advantage), user)
    return {'skill':data.skill,'skill_name':result['name'],'ability':result['ability'],'roll':result['roll'],
            'ability_modifier':result['modifier'],'proficiency_bonus':result['proficiency'],'total':result['total'],
            'dc':result['target'],'success':result['success'],'critical':False,'critical_failure':False,'level':level_for(user)}
