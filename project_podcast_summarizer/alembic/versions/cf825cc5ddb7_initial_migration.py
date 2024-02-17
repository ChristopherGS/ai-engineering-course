"""initial migration

Revision ID: cf825cc5ddb7
Revises: 
Create Date: 2024-02-17 10:44:47.781143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf825cc5ddb7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=256), nullable=False),
    sa.Column('url', sa.String(length=256), nullable=True),
    sa.Column('source', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_id'), 'recipe', ['id'], unique=False)
    op.create_index(op.f('ix_recipe_url'), 'recipe', ['url'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_recipe_url'), table_name='recipe')
    op.drop_index(op.f('ix_recipe_id'), table_name='recipe')
    op.drop_table('recipe')
    # ### end Alembic commands ###
