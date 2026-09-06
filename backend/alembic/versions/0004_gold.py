from alembic import op
import sqlalchemy as sa
revision='0004_gold';down_revision='0003_character';branch_labels=None;depends_on=None
def upgrade():
 op.add_column('users',sa.Column('gold',sa.Integer(),nullable=False,server_default='100'))
def downgrade():
 op.drop_column('users','gold')
