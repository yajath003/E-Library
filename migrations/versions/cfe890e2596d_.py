"""empty message

Revision ID: cfe890e2596d
Revises: 
Create Date: 2024-05-10 12:03:46.468814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfe890e2596d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('accept', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_valid_date', sa.Date(), nullable=False))
        batch_op.alter_column('issued_date',
               existing_type=sa.DATETIME(),
               type_=sa.Date(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('accept', schema=None) as batch_op:
        batch_op.alter_column('issued_date',
               existing_type=sa.Date(),
               type_=sa.DATETIME(),
               existing_nullable=False)
        batch_op.drop_column('_valid_date')

    # ### end Alembic commands ###
