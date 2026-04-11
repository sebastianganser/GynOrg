#!/usr/bin/env python3
"""
Script to create default absence types in the database.
Run this script to populate the absence_types table with standard types.
"""

import asyncio
from sqlmodel import Session, select
from app.core.database import engine
from app.models.absence_type import AbsenceType, AbsenceTypeCategory


async def create_default_absence_types():
    """Create default absence types if they don't exist."""
    
    default_types = [
        {
            "name": "Urlaub",
            "category": AbsenceTypeCategory.VACATION,
            "color": "#10B981",  # Green
            "is_paid": True,
            "requires_approval": False,
            "description": "Regulärer Jahresurlaub"
        },
        {
            "name": "Krankheit",
            "category": AbsenceTypeCategory.SICK_LEAVE,
            "color": "#EF4444",  # Red
            "is_paid": True,
            "requires_approval": False,
            "description": "Krankheitsbedingte Abwesenheit"
        },
        {
            "name": "Fortbildung",
            "category": AbsenceTypeCategory.TRAINING,
            "color": "#3B82F6",  # Blue
            "is_paid": True,
            "requires_approval": False,
            "description": "Berufliche Weiterbildung und Schulungen"
        },
        {
            "name": "Sonderurlaub",
            "category": AbsenceTypeCategory.SPECIAL_LEAVE,
            "color": "#8B5CF6",  # Purple
            "is_paid": True,
            "requires_approval": False,
            "max_days_per_request": 5,
            "description": "Sonderurlaub für besondere Anlässe"
        },
        {
            "name": "Kind krank",
            "category": AbsenceTypeCategory.SICK_LEAVE,
            "color": "#F59E0B",  # Amber
            "is_paid": True,
            "requires_approval": False,
            "max_days_per_request": 10,
            "description": "Betreuung kranker Kinder"
        }
    ]
    
    with Session(engine) as session:
        print("Creating default absence types...")
        
        for type_data in default_types:
            # Check if absence type already exists
            statement = select(AbsenceType).where(
                AbsenceType.name == type_data["name"]
            )
            existing_type = session.exec(statement).first()
            
            if existing_type:
                print(f"✓ Absence type '{type_data['name']}' already exists")
                continue
            
            # Create new absence type
            absence_type = AbsenceType(**type_data)
            session.add(absence_type)
            print(f"✓ Created absence type: {type_data['name']}")
        
        session.commit()
        print("\n✅ Default absence types created successfully!")
        
        # Display all absence types
        print("\n📋 Current absence types:")
        statement = select(AbsenceType).where(AbsenceType.active == True)
        all_types = session.exec(statement).all()
        
        for absence_type in all_types:
            print(f"  - {absence_type.name} ({absence_type.category.value}) - {absence_type.color}")


if __name__ == "__main__":
    asyncio.run(create_default_absence_types())
