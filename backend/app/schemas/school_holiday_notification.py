from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from backend.app.models.school_holiday_notification import NotificationType


class SchoolHolidayNotificationBase(BaseModel):
    """Base schema for school holiday notifications"""
    employee_id: int = Field(..., description="ID of the employee")
    holiday_id: int = Field(..., description="ID of the holiday")
    notification_type: NotificationType = Field(..., description="Type of notification")
    scheduled_date: datetime = Field(..., description="When the notification should be sent")
    message: str = Field(..., description="Notification message")

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Validate message is not empty"""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message cannot be longer than 1000 characters")
        return v.strip()


class SchoolHolidayNotificationCreate(SchoolHolidayNotificationBase):
    """Schema for creating school holiday notifications"""
    pass


class SchoolHolidayNotificationUpdate(BaseModel):
    """Schema for updating school holiday notifications"""
    notification_type: Optional[NotificationType] = None
    scheduled_date: Optional[datetime] = None
    message: Optional[str] = None
    is_sent: Optional[bool] = None

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Validate message is not empty"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Message cannot be empty")
            if len(v) > 1000:
                raise ValueError("Message cannot be longer than 1000 characters")
        return v.strip() if v else v


class SchoolHolidayNotificationRead(SchoolHolidayNotificationBase):
    """Schema for reading school holiday notifications"""
    id: int
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SchoolHolidayNotificationResponse(BaseModel):
    """Response schema for school holiday notifications"""
    id: int
    employee_id: int
    holiday_id: int
    notification_type: str
    scheduled_date: datetime
    message: str
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime
    
    # Computed fields
    is_pending: bool = Field(..., description="Whether notification is pending")
    is_overdue: bool = Field(..., description="Whether notification is overdue")
    priority: int = Field(..., description="Notification priority (lower = higher priority)")
    
    # Related data
    holiday_name: Optional[str] = None
    holiday_date: Optional[datetime] = None
    employee_name: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, notification, include_related: bool = False):
        """Create response from model instance"""
        response_data = {
            'id': notification.id,
            'employee_id': notification.employee_id,
            'holiday_id': notification.holiday_id,
            'notification_type': notification.notification_type.value,
            'scheduled_date': notification.scheduled_date,
            'message': notification.message,
            'is_sent': notification.is_sent,
            'sent_at': notification.sent_at,
            'created_at': notification.created_at,
            'is_pending': notification.is_pending,
            'is_overdue': notification.is_overdue,
            'priority': notification.get_notification_priority()
        }
        
        if include_related:
            if hasattr(notification, 'holiday') and notification.holiday:
                response_data['holiday_name'] = notification.holiday.name
                response_data['holiday_date'] = notification.holiday.date
            
            if hasattr(notification, 'employee') and notification.employee:
                response_data['employee_name'] = notification.employee.full_name
        
        return cls(**response_data)


class SchoolHolidayNotificationFilter(BaseModel):
    """Filter schema for school holiday notifications"""
    employee_id: Optional[int] = None
    holiday_id: Optional[int] = None
    notification_type: Optional[NotificationType] = None
    is_sent: Optional[bool] = None
    is_pending: Optional[bool] = None
    is_overdue: Optional[bool] = None
    scheduled_after: Optional[datetime] = None
    scheduled_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class SchoolHolidayNotificationBulkCreate(BaseModel):
    """Schema for bulk creating notifications"""
    notifications: List[SchoolHolidayNotificationCreate]
    
    @field_validator('notifications')
    @classmethod
    def validate_notifications(cls, v):
        """Validate notifications list is not empty"""
        if not v:
            raise ValueError("Notifications list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot create more than 100 notifications at once")
        return v


class SchoolHolidayNotificationBulkUpdate(BaseModel):
    """Schema for bulk updating notifications"""
    notification_ids: List[int] = Field(..., description="List of notification IDs to update")
    update_data: SchoolHolidayNotificationUpdate = Field(..., description="Update data to apply")
    
    @field_validator('notification_ids')
    @classmethod
    def validate_notification_ids(cls, v):
        """Validate notification IDs list"""
        if not v:
            raise ValueError("Notification IDs list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot update more than 100 notifications at once")
        return v


class SchoolHolidayNotificationStats(BaseModel):
    """Statistics schema for notifications"""
    total_notifications: int
    pending_notifications: int
    sent_notifications: int
    overdue_notifications: int
    notifications_by_type: dict[str, int]
    notifications_by_employee: dict[int, int]
    upcoming_notifications_7_days: int
    upcoming_notifications_30_days: int


class SchoolHolidayNotificationSummary(BaseModel):
    """Summary schema for notifications"""
    employee_id: int
    employee_name: str
    total_notifications: int
    pending_notifications: int
    sent_notifications: int
    overdue_notifications: int
    next_notification_date: Optional[datetime] = None
    last_notification_sent: Optional[datetime] = None

    class Config:
        from_attributes = True


class UpcomingHolidayNotificationRequest(BaseModel):
    """Request schema for creating upcoming holiday notifications"""
    employee_id: int = Field(..., description="Employee ID")
    holiday_id: int = Field(..., description="Holiday ID")
    days_advance: int = Field(default=14, description="Days in advance to send notification")
    
    @field_validator('days_advance')
    @classmethod
    def validate_days_advance(cls, v):
        """Validate days advance"""
        if v < 1 or v > 365:
            raise ValueError("Days advance must be between 1 and 365")
        return v


class ConflictNotificationRequest(BaseModel):
    """Request schema for creating conflict notifications"""
    employee_id: int = Field(..., description="Employee ID")
    holiday_id: int = Field(..., description="Holiday ID")
    conflict_description: str = Field(..., description="Description of the conflict")
    
    @field_validator('conflict_description')
    @classmethod
    def validate_conflict_description(cls, v):
        """Validate conflict description"""
        if not v or not v.strip():
            raise ValueError("Conflict description cannot be empty")
        if len(v) > 500:
            raise ValueError("Conflict description cannot be longer than 500 characters")
        return v.strip()


class SuggestionNotificationRequest(BaseModel):
    """Request schema for creating suggestion notifications"""
    employee_id: int = Field(..., description="Employee ID")
    holiday_id: int = Field(..., description="Holiday ID")
    suggestion: str = Field(..., description="Suggestion text")
    
    @field_validator('suggestion')
    @classmethod
    def validate_suggestion(cls, v):
        """Validate suggestion"""
        if not v or not v.strip():
            raise ValueError("Suggestion cannot be empty")
        if len(v) > 500:
            raise ValueError("Suggestion cannot be longer than 500 characters")
        return v.strip()


class NotificationSendResult(BaseModel):
    """Result schema for sending notifications"""
    notification_id: int
    success: bool
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


class NotificationBulkSendResult(BaseModel):
    """Result schema for bulk sending notifications"""
    total_attempted: int
    successful_sends: int
    failed_sends: int
    results: List[NotificationSendResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_attempted == 0:
            return 0.0
        return (self.successful_sends / self.total_attempted) * 100
