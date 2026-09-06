from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..auth import current_user
from ..db import get_db
from ..dnd_rules import SKILLS, ability_check, character_derived
from ..models import User

router = APIRouter(prefix='/api', tags=['rules'])


class CheckIn(BaseModel):
    skill: str = Field(min_length=1, max_length=64)
    dc: int = Field(ge=1, le=30)
    advantage: int = Field(default=0, ge=-1, le=1)


@router.get('/character/sheet')
def character_sheet(user: User = Depends(current_user)):
    if not user.character_name:
        raise HTTPException(404, 'Персонаж не создан')
    stats = {
        'strength': user.strength or 10,
        'dexterity': user.dexterity or 10,
        'constitution': user.constitution or 10,
        'intelligence': user.intelligence or 10,
        'wisdom': user.wisdom or 10,
        'charisma': user.charisma or 10,
    }
    level = max(1, (user.xp // 250) + 1)
    return {
        'character': {
            'name': user.character_name,
            'race': user.character_race,
            'class': user.character_class,
            'background': user.character_background,
            'stats': stats,
        },
        'derived': character_derived(stats, user.character_class or '', level),
    }


@router.post('/check')
def make_check(data: CheckIn, user: User = Depends(current_user)):
    if not user.character_name:
        raise HTTPException(400, 'Сначала создай персонажа')
    skill = SKILLS.get(data.skill)
    if not skill:
        raise HTTPException(404, 'Навык не найден')
    ability, name = skill
    score = getattr(user, ability) or 10
    level = max(1, (user.xp // 250) + 1)
    character_class = user.character_class or ''
    proficient = data.skill in character_derived({k: getattr(user, k) or 10 for k in ('strength','dexterity','constitution','intelligence','wisdom','charisma')}, character_class, level)['skill_proficiencies']
    result = ability_check(score, data.dc, proficient=proficient, level=level, advantage=data.advantage)
    return {
        'skill': data.skill,
        'skill_name': name,
        'ability': ability,
        'roll': result.roll,
        'ability_modifier': result.modifier,
        'proficiency_bonus': result.proficiency,
        'total': result.total,
        'dc': result.dc,
        'success': result.success,
        'critical': result.critical,
        'critical_failure': result.critical_failure,
        'level': level,
    }
