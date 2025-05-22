from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID

@dataclass
class GenerateAccessCodeCommand:
    """Command for generating an access code"""
    referral_email: str=None
    referral_phone: Optional[str] = None
    health_care_center_email: Optional[str] = None  # Email to find an existing center
    health_care_center_phone: Optional[str] = None  # Phone to find an existing center
    expiry_days: Optional[int] = 7  # Default expiry of 7 days 