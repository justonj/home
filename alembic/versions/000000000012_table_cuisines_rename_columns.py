'''rename table cuisines column'''

# revision identifiers, used by Alembic.
revision = '000000000012'
down_revision = '000000000011'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa



def upgrade():
    op.execute("""
        ALTER TABLE cuisines RENAME column cuisine_name TO name;
        """)
    op.execute("""
        ALTER TABLE cuisines RENAME column yelp_input TO category;
        """)
    op.execute("CREATE INDEX ON cuisines (name);")


def downgrade():
    op.execute("""
        ALTER TABLE cuisines RENAME column name TO cuisine_name;
        """)
    op.execute("""
        ALTER TABLE cuisines RENAME column category TO yelp_input;
        """)
