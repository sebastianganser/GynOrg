import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

try:
    from app.models.station import Station, StationCapacity
    from app.models.auslastung import DailyEntry
    from app.models.auslastung_tag import CalendarTag, DayTag
    print("Imports successful!")
except Exception as e:
    import traceback
    traceback.print_exc()

print("Ready.")
