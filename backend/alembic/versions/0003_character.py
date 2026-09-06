from alembic import op
import sqlalchemy as sa
revision='0003_character';down_revision='0002_dnd_entities';branch_labels=None;depends_on=None
def upgrade():
 for name,size in [('character_name',80),('character_race',80),('character_class',80),('character_background',160)]:op.add_column('users',sa.Column(name,sa.String(size),nullable=True))
 for name in ['strength','dexterity','constitution','intelligence','wisdom','charisma']:op.add_column('users',sa.Column(name,sa.Integer(),nullable=True))
def downgrade():
 for name in ['charisma','wisdom','intelligence','constitution','dexterity','strength','character_background','character_class','character_race','character_name']:op.drop_column('users',name)
