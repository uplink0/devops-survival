from alembic import op
import sqlalchemy as sa
revision='0001_initial';down_revision=None;branch_labels=None;depends_on=None
def upgrade():
 op.create_table('users',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('username',sa.String(32),nullable=False),sa.Column('email',sa.String(255),nullable=False),sa.Column('password_hash',sa.String(255),nullable=False),sa.Column('xp',sa.Integer(),nullable=False,server_default='0'),sa.Column('streak',sa.Integer(),nullable=False,server_default='0'),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False));op.create_index('ix_users_username','users',['username'],unique=True);op.create_index('ix_users_email','users',['email'],unique=True)
 op.create_table('progress',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),sa.Column('incident_id',sa.String(64),nullable=False),sa.Column('solved',sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column('best_score',sa.Integer(),nullable=False,server_default='0'),sa.Column('attempts',sa.Integer(),nullable=False,server_default='0'),sa.Column('last_played',sa.DateTime(timezone=True),nullable=False));op.create_index('ix_progress_user_id','progress',['user_id']);op.create_index('ix_progress_incident_id','progress',['incident_id'])
def downgrade():
 op.drop_table('progress');op.drop_index('ix_users_email','users');op.drop_index('ix_users_username','users');op.drop_table('users')
