from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dataBase import db
class AddressModel(db.Model):
    __tablename__ = "addresses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    building_number: Mapped[str] = mapped_column(String(50), nullable=True)
    apartment_number: Mapped[str] = mapped_column(String(50), nullable=True)
    additional_info: Mapped[str] = mapped_column(Text, nullable=True)
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    health_care_center_id: Mapped[UUID] = mapped_column(
        ForeignKey("health_care_centers.id"), 
        nullable=True, 
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("UserModel", back_populates="addresses")
    health_care_center = relationship("HealthCareCenterModel", back_populates="addresses")

    # __table_args__ = (
    #     # Ensure address belongs to either user or health care center, not both
    #     # This is a business rule enforced at the database level
    #     CheckConstraint(
    #         "(user_id IS NULL AND health_care_center_id IS NOT NULL) OR "
    #         "(user_id IS NOT NULL AND health_care_center_id IS NULL)",
    #         name="address_owner_check"
    #     ),
    # )
