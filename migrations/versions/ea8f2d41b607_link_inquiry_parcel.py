"""Store the selected parcel independently of the investor's purpose."""
from alembic import op
import sqlalchemy as sa

revision = "ea8f2d41b607"
down_revision = "923a585c728f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("inquiries") as batch:
        batch.add_column(sa.Column("selected_parcel_id", sa.String(), nullable=True))
        batch.create_foreign_key(
            "fk_inquiries_selected_parcel", "parcels", ["selected_parcel_id"],
            ["parcel_id"], ondelete="SET NULL"
        )
        batch.create_index("ix_inquiries_selected_parcel_id", ["selected_parcel_id"])


def downgrade():
    with op.batch_alter_table("inquiries") as batch:
        batch.drop_index("ix_inquiries_selected_parcel_id")
        batch.drop_constraint("fk_inquiries_selected_parcel", type_="foreignkey")
        batch.drop_column("selected_parcel_id")
