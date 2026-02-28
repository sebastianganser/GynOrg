from typing import List, Optional
import os
import io
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from PIL import Image
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user
from app.models.employee import Employee, EmployeeCreate, EmployeeUpdate
from app.models.vacation_allowance import VacationAllowance
from app.models.federal_state import FederalState
from app.schemas.employee_calendar import EmployeeCalendarInfo

router = APIRouter()


@router.get("/", response_model=List[Employee])
def get_employees(
    active_only: bool = Query(True, description="Filter for active employees only"),
    federal_state: Optional[FederalState] = Query(None, description="Filter by federal state"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all employees with optional filtering"""
    statement = select(Employee)
    
    if active_only:
        statement = statement.where(Employee.active == True)
    
    if federal_state:
        statement = statement.where(Employee.federal_state == federal_state)
    
    # Add pagination
    offset = (page - 1) * per_page
    statement = statement.offset(offset).limit(per_page)
    
    employees = session.exec(statement).all()
    return employees


@router.get("/calendar-list", response_model=List[EmployeeCalendarInfo])
def get_employees_for_calendar(
    active_only: bool = Query(True, description="Filter for active employees only"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get simplified employee list for calendar sidebar
    Returns only essential information: ID, name, calendar color, and active status
    """
    statement = select(Employee)
    
    if active_only:
        statement = statement.where(Employee.active == True)
    
    # Order by last name, then first name for consistent display
    statement = statement.order_by(Employee.last_name, Employee.first_name)
    
    employees = session.exec(statement).all()
    
    # Transform to calendar info format
    calendar_employees = []
    for emp in employees:
        calendar_employees.append(
            EmployeeCalendarInfo(
                id=emp.id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                full_name=emp.full_name,
                calendar_color=emp.calendar_color or "#3b82f6",  # Default blue if not set
                active=emp.active
            )
        )
    
    return calendar_employees


@router.get("/search", response_model=List[Employee])
def search_employees(
    query: str = Query(..., min_length=2, description="Search query for name or email"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Search employees by name or email"""
    statement = select(Employee).where(
        (Employee.first_name.ilike(f"%{query}%")) |
        (Employee.last_name.ilike(f"%{query}%")) |
        (Employee.email.ilike(f"%{query}%"))
    ).where(Employee.active == True)
    
    employees = session.exec(statement).all()
    return employees


@router.get("/by-federal-state/{federal_state}", response_model=List[Employee])
def get_employees_by_federal_state(
    federal_state: FederalState,
    active_only: bool = Query(True, description="Filter for active employees only"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get employees by federal state"""
    statement = select(Employee).where(Employee.federal_state == federal_state)
    
    if active_only:
        statement = statement.where(Employee.active == True)
    
    employees = session.exec(statement).all()
    return employees


@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific employee by ID"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return employee


@router.get("/{employee_id}/vacation-allowances", response_model=List[VacationAllowance])
def get_employee_vacation_allowances(
    employee_id: int,
    year: Optional[int] = Query(None, description="Filter by specific year"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get vacation allowances for a specific employee"""
    # Check if employee exists
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    statement = select(VacationAllowance).where(VacationAllowance.employee_id == employee_id)
    
    if year:
        statement = statement.where(VacationAllowance.year == year)
    
    allowances = session.exec(statement).all()
    return allowances


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new employee"""
    # Check if email already exists
    existing_employee = session.exec(
        select(Employee).where(Employee.email == employee_data.email)
    ).first()
    
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists"
        )
    
    employee = Employee(**employee_data.model_dump())
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing employee"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check email uniqueness if email is being updated
    update_data = employee_data.model_dump(exclude_unset=True)
    if "email" in update_data:
        existing_employee = session.exec(
            select(Employee).where(
                Employee.email == update_data["email"],
                Employee.id != employee_id
            )
        ).first()
        
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this email already exists"
            )
    
    # Update only provided fields
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Soft delete an employee (set active=False)"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Soft delete by setting active to False
    employee.active = False
    session.add(employee)
    session.commit()
    return None


@router.delete("/{employee_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Hard delete an employee (permanently remove from database)"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Delete profile image if exists
    if employee.profile_image_path and os.path.exists(employee.profile_image_path):
        os.remove(employee.profile_image_path)
    
    # Manually delete related records to prevent foreign key errors (robust fallback)
    from sqlmodel import delete
    from app.models.school_holiday_notification import SchoolHolidayNotification
    from app.models.absence import Absence
    from app.models.vacation_allowance import VacationAllowance
    from app.models.vacation_entitlement import VacationEntitlement

    session.exec(delete(SchoolHolidayNotification).where(SchoolHolidayNotification.employee_id == employee_id))
    session.exec(delete(Absence).where(Absence.employee_id == employee_id))
    session.exec(delete(VacationAllowance).where(VacationAllowance.employee_id == employee_id))
    session.exec(delete(VacationEntitlement).where(VacationEntitlement.employee_id == employee_id))

    session.delete(employee)
    session.commit()
    return None


@router.post("/{employee_id}/avatar", response_model=Employee)
async def upload_avatar(
    employee_id: int,
    file: UploadFile = File(...),
    crop_x: Optional[float] = Form(None),
    crop_y: Optional[float] = Form(None),
    crop_width: Optional[float] = Form(None),
    crop_height: Optional[float] = Form(None),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Upload avatar image for employee"""
    # Check if employee exists
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files (JPEG, PNG, GIF, WebP) are allowed"
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Use an absolute path inside the container: /app/uploads/profiles
    # This matches the volume mapping ./data/uploads:/app/uploads
    upload_dir = "/app/uploads/profiles"
    if not os.path.exists("/app"):
        # Fallback for local testing (without docker)
        upload_dir = "uploads/profiles"
        
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    # Delete old profile image if exists
    if employee.profile_image_path and os.path.exists(employee.profile_image_path):
        os.remove(employee.profile_image_path)
    
    # Process and save image
    if crop_width and crop_height:
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Convert percentage coordinates to pixels
            img_width, img_height = image.size
            x0 = int((crop_x or 0) * img_width / 100)
            y0 = int((crop_y or 0) * img_height / 100)
            x1 = x0 + int(crop_width * img_width / 100)
            y1 = y0 + int(crop_height * img_height / 100)
            
            # Crop image
            cropped_image = image.crop((x0, y0, x1, y1))
            
            # Convert to RGB (in case of PNG with alpha) before saving as JPEG or similar uniformly
            if cropped_image.mode in ("RGBA", "P"):
                cropped_image = cropped_image.convert("RGB")
                
            # Resize
            cropped_image.thumbnail((256, 256), Image.Resampling.LANCZOS)
            
            # Save optimized
            cropped_image.save(file_path, format="JPEG", quality=85, optimize=True)
            
            # Force filename to be jpg since we converted
            file_extension = "jpg"
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            cropped_image.save(file_path, format="JPEG", quality=85, optimize=True)
            
        except Exception as e:
            print(f"Error cropping image: {e}")
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
    else:
        # Save original file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    
    # Update employee record
    employee.profile_image_path = file_path
    session.add(employee)
    session.commit()
    session.refresh(employee)
    
    return employee


@router.get("/{employee_id}/avatar")
async def get_avatar(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get avatar image for employee"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if not employee.profile_image_path or not os.path.exists(employee.profile_image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )
    
    return FileResponse(
        employee.profile_image_path,
        media_type="image/jpeg",
        filename=f"avatar_{employee_id}.jpg"
    )


@router.delete("/{employee_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete avatar image for employee"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if employee.profile_image_path and os.path.exists(employee.profile_image_path):
        os.remove(employee.profile_image_path)
    
    employee.profile_image_path = None
    session.add(employee)
    session.commit()
    
    return None


@router.put("/{employee_id}/initials", response_model=Employee)
def update_initials(
    employee_id: int,
    initials: str = Query(..., max_length=3, description="Employee initials (max 3 characters)"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update employee initials for avatar fallback"""
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    employee.initials = initials.upper()
    session.add(employee)
    session.commit()
    session.refresh(employee)
    
    return employee
