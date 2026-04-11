from typing import List
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.federal_state import FederalState

router = APIRouter()


@router.get("/", response_model=List[str])
def get_federal_states(
    current_user: dict = Depends(get_current_user)
):
    """Get all available German federal states"""
    return [state.value for state in FederalState]


@router.get("/enum", response_model=List[dict])
def get_federal_states_with_details(
    current_user: dict = Depends(get_current_user)
):
    """Get all federal states with their enum values and display names"""
    return [
        {
            "value": state.value,
            "name": state.name,
            "display_name": state.value
        }
        for state in FederalState
    ]
