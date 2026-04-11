from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum


class NotificationType(str, enum.Enum):
    UPCOMING = "UPCOMING"
    CONFLICT = "CONFLICT"
    SUGGESTION = "SUGGESTION"


if TYPE_CHECKING:
    from .employee import Employee
    from .holiday import Holiday


class SchoolHolidayNotification(SQLModel, table=True):
    __tablename__ = "school_holiday_notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id", index=True)
    holiday_id: int = Field(foreign_key="holidays.id", index=True)
    notification_type: NotificationType = Field(index=True)
    scheduled_date: datetime = Field(index=True)
    message: str = Field()
    is_sent: bool = Field(default=False, index=True)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    # Relationships
    employee: Optional["Employee"] = Relationship()
    # Fix: Use employee_id to link to preferences via Employee relationship
    # employee_preferences: Optional["EmployeeSchoolHolidayPreferences"] = Relationship(back_populates="notifications")

    def __repr__(self):
        return f"<SchoolHolidayNotification(id={self.id}, employee_id={self.employee_id}, type={self.notification_type.value}, sent={self.is_sent})>"

    @property
    def is_pending(self) -> bool:
        """Check if notification is pending (not sent and scheduled date not passed)."""
        return not self.is_sent and self.scheduled_date > datetime.now()

    @property
    def is_overdue(self) -> bool:
        """Check if notification is overdue (not sent but scheduled date has passed)."""
        return not self.is_sent and self.scheduled_date <= datetime.now()

    def mark_as_sent(self) -> None:
        """Mark notification as sent with current timestamp."""
        self.is_sent = True
        self.sent_at = datetime.now()

    def can_be_sent(self) -> bool:
        """Check if notification can be sent (not already sent and scheduled time has arrived)."""
        return not self.is_sent and self.scheduled_date <= datetime.now()

    def get_notification_priority(self) -> int:
        """Get notification priority for sorting (lower number = higher priority)."""
        priority_map = {
            NotificationType.CONFLICT: 1,
            NotificationType.UPCOMING: 2,
            NotificationType.SUGGESTION: 3
        }
        return priority_map.get(self.notification_type, 999)

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'holiday_id': self.holiday_id,
            'notification_type': self.notification_type.value,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'message': self.message,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_pending': self.is_pending,
            'is_overdue': self.is_overdue,
            'priority': self.get_notification_priority()
        }

    @classmethod
    def create_upcoming_notification(
        cls,
        employee_id: int,
        holiday_id: int,
        holiday_name: str,
        holiday_date: datetime,
        days_advance: int = 14
    ) -> 'SchoolHolidayNotification':
        """
        Create an upcoming holiday notification.
        
        Args:
            employee_id: ID of the employee
            holiday_id: ID of the holiday
            holiday_name: Name of the holiday
            holiday_date: Date of the holiday
            days_advance: Days before holiday to send notification
            
        Returns:
            SchoolHolidayNotification: New notification instance
        """
        from datetime import timedelta
        
        scheduled_date = holiday_date - timedelta(days=days_advance)
        message = f"Erinnerung: {holiday_name} beginnt in {days_advance} Tagen am {holiday_date.strftime('%d.%m.%Y')}. Möchten Sie Urlaub beantragen?"
        
        return cls(
            employee_id=employee_id,
            holiday_id=holiday_id,
            notification_type=NotificationType.UPCOMING,
            scheduled_date=scheduled_date,
            message=message
        )

    @classmethod
    def create_conflict_notification(
        cls,
        employee_id: int,
        holiday_id: int,
        holiday_name: str,
        conflict_description: str
    ) -> 'SchoolHolidayNotification':
        """
        Create a conflict notification.
        
        Args:
            employee_id: ID of the employee
            holiday_id: ID of the holiday
            holiday_name: Name of the holiday
            conflict_description: Description of the conflict
            
        Returns:
            SchoolHolidayNotification: New notification instance
        """
        message = f"Konflikt erkannt: {holiday_name} - {conflict_description}"
        
        return cls(
            employee_id=employee_id,
            holiday_id=holiday_id,
            notification_type=NotificationType.CONFLICT,
            scheduled_date=datetime.now(),
            message=message
        )

    @classmethod
    def create_suggestion_notification(
        cls,
        employee_id: int,
        holiday_id: int,
        holiday_name: str,
        suggestion: str
    ) -> 'SchoolHolidayNotification':
        """
        Create a suggestion notification.
        
        Args:
            employee_id: ID of the employee
            holiday_id: ID of the holiday
            holiday_name: Name of the holiday
            suggestion: Suggestion text
            
        Returns:
            SchoolHolidayNotification: New notification instance
        """
        message = f"Urlaubstipp: {holiday_name} - {suggestion}"
        
        return cls(
            employee_id=employee_id,
            holiday_id=holiday_id,
            notification_type=NotificationType.SUGGESTION,
            scheduled_date=datetime.now(),
            message=message
        )
