from alembic import op
import sqlalchemy as sa
revision='0002_dnd_entities';down_revision='0001_initial';branch_labels=None;depends_on=None
def upgrade():
 op.add_column('users',sa.Column('avatar_url',sa.String(512),nullable=True))
 op.create_table('inventory_items',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('item_key',sa.String(64),nullable=False),sa.Column('name',sa.String(120),nullable=False),sa.Column('icon',sa.String(16),nullable=False,server_default='📦'),sa.Column('quantity',sa.Integer(),nullable=False,server_default='1'),sa.Column('description',sa.String(500),nullable=True));op.create_index('ix_inventory_items_user_id','inventory_items',['user_id'])
 op.create_table('companions',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('name',sa.String(80),nullable=False),sa.Column('role',sa.String(80),nullable=False),sa.Column('emoji',sa.String(16),nullable=False,server_default='🧙'),sa.Column('description',sa.String(500),nullable=True),sa.Column('hp',sa.Integer(),nullable=False,server_default='100'));op.create_index('ix_companions_user_id','companions',['user_id'])
 op.create_table('chat_messages',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('role',sa.String(20),nullable=False),sa.Column('content',sa.Text(),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False));op.create_index('ix_chat_messages_user_id','chat_messages',['user_id'])
def downgrade():
 op.drop_table('chat_messages');op.drop_table('companions');op.drop_table('inventory_items');op.drop_column('users','avatar_url')
