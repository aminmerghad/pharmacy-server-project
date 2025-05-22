from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

@dataclass
class PrescriptionItem:
    id: UUID
    medication_id: UUID
    dosage: str
    frequency: str
    duration: str
    quantity: int
    instructions: str
    refills_remaining: int

@dataclass
class Prescription:
    id: UUID
    doctor_id: UUID
    patient_id: UUID
    prescription_date: datetime
    expiry_date: datetime
    items: List[PrescriptionItem]
    notes: str
    is_valid: bool
    verification_status: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        doctor_id: UUID,
        patient_id: UUID,
        items: List[PrescriptionItem],
        notes: str = "",
        expiry_days: int = 30
    ) -> 'Prescription':
        now = datetime.utcnow()
        return Prescription(
            id=uuid4(),
            doctor_id=doctor_id,
            patient_id=patient_id,
            prescription_date=now,
            expiry_date=now + datetime.timedelta(days=expiry_days),
            items=items,
            notes=notes,
            is_valid=True,
            verification_status="PENDING",
            created_at=now,
            updated_at=now
        )

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expiry_date

    def has_refills(self, medication_id: UUID) -> bool:
        item = next((item for item in self.items if item.medication_id == medication_id), None)
        return item is not None and item.refills_remaining > 0

    def use_refill(self, medication_id: UUID) -> bool:
        item = next((item for item in self.items if item.medication_id == medication_id), None)
        if item and item.refills_remaining > 0:
            item.refills_remaining -= 1
            self.updated_at = datetime.utcnow()
            return True
        return False

    def verify(self) -> None:
        self.verification_status = "VERIFIED"
        self.updated_at = datetime.utcnow()

    def invalidate(self) -> None:
        self.is_valid = False
        self.updated_at = datetime.utcnow() 