"""
School Holiday API Client for mehr-schulferien.de API v2.1

This client handles communication with the mehr-schulferien.de API to fetch
German school holiday data for all 16 federal states.
"""
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..models.holiday import SchoolVacationType, DataSource
from ..models.federal_state import FederalState
from ..core.config import settings

logger = logging.getLogger(__name__)


class SchoolHolidayApiError(Exception):
    """Base exception for School Holiday API errors"""
    pass


class SchoolHolidayApiRateLimitError(SchoolHolidayApiError):
    """Raised when API rate limit is exceeded"""
    pass


class SchoolHolidayApiTimeoutError(SchoolHolidayApiError):
    """Raised when API request times out"""
    pass


class SchoolHolidayApiClient:
    """
    Robust API client for mehr-schulferien.de API v2.1
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limiting respect
    - Comprehensive error handling
    - Logging and metrics
    - Bulk data retrieval support
    """
    
    BASE_URL = "https://www.mehr-schulferien.de/api/v2.1/federal-states"
    
    # Mapping from FederalState enum to mehr-schulferien.de URL segments
    BUNDESLAND_MAPPING = {
        FederalState.BADEN_WUERTTEMBERG: "baden-wuerttemberg",
        FederalState.BAYERN: "bayern", 
        FederalState.BERLIN: "berlin",
        FederalState.BRANDENBURG: "brandenburg",
        FederalState.BREMEN: "bremen",
        FederalState.HAMBURG: "hamburg",
        FederalState.HESSEN: "hessen",
        FederalState.MECKLENBURG_VORPOMMERN: "mecklenburg-vorpommern",
        FederalState.NIEDERSACHSEN: "niedersachsen",
        FederalState.NORDRHEIN_WESTFALEN: "nordrhein-westfalen",
        FederalState.RHEINLAND_PFALZ: "rheinland-pfalz",
        FederalState.SAARLAND: "saarland",
        FederalState.SACHSEN: "sachsen",
        FederalState.SACHSEN_ANHALT: "sachsen-anhalt",
        FederalState.SCHLESWIG_HOLSTEIN: "schleswig-holstein",
        FederalState.THUERINGEN: "thueringen"
    }
    
    # Mapping from mehr-schulferien.de vacation names to our SchoolVacationType enum
    VACATION_TYPE_MAPPING = {
        "Winter": SchoolVacationType.WINTER,
        "Winterferien": SchoolVacationType.WINTER,
        "Ostern": SchoolVacationType.EASTER,
        "Osterferien": SchoolVacationType.EASTER,
        "Pfingsten": SchoolVacationType.PENTECOST,
        "Pfingstferien": SchoolVacationType.PENTECOST,
        "Sommer": SchoolVacationType.SUMMER,
        "Sommerferien": SchoolVacationType.SUMMER,
        "Herbst": SchoolVacationType.AUTUMN,
        "Herbstferien": SchoolVacationType.AUTUMN,
        "Weihnachten": SchoolVacationType.CHRISTMAS,
        "Weihnachtsferien": SchoolVacationType.CHRISTMAS,
    }
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the API client
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session_stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retries_used": 0,
            "total_holidays_fetched": 0
        }
        
        # HTTP client configuration
        self.client_config = {
            "timeout": httpx.Timeout(timeout),
            "limits": httpx.Limits(max_keepalive_connections=5, max_connections=10),
            "headers": {
                "User-Agent": f"{settings.PROJECT_NAME}/{settings.PROJECT_VERSION} School Holiday Sync",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate"
            }
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, SchoolHolidayApiRateLimitError))
    )
    async def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            SchoolHolidayApiError: For various API errors
        """
        self.session_stats["requests_made"] += 1
        
        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                logger.debug(f"Making request to {url} with params {params}")
                
                response = await client.get(url, params=params)
                
                # Handle rate limiting
                if response.status_code == 429:
                    self.session_stats["retries_used"] += 1
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    raise SchoolHolidayApiRateLimitError(f"Rate limited, retry after {retry_after}s")
                
                # Handle other HTTP errors
                if response.status_code >= 400:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"API request failed: {error_msg}")
                    self.session_stats["failed_requests"] += 1
                    raise SchoolHolidayApiError(error_msg)
                
                # Parse JSON response
                try:
                    data = response.json()
                    self.session_stats["successful_requests"] += 1
                    logger.debug(f"Successfully fetched {len(data) if isinstance(data, list) else 1} items")
                    return data
                    
                except ValueError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    self.session_stats["failed_requests"] += 1
                    raise SchoolHolidayApiError(f"Invalid JSON response: {e}")
                    
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            self.session_stats["failed_requests"] += 1
            raise SchoolHolidayApiTimeoutError(f"Request timeout: {e}")
            
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            self.session_stats["failed_requests"] += 1
            raise SchoolHolidayApiError(f"Connection error: {e}")
    
    async def fetch_school_holidays(self, federal_state: FederalState, year: int) -> List[Dict[str, Any]]:
        """
        Fetch school holidays for a specific federal state and year
        
        Args:
            federal_state: German federal state
            year: Year to fetch holidays for
            
        Returns:
            List of school holiday data dictionaries
            
        Raises:
            SchoolHolidayApiError: If API request fails
        """
        # Get URL segment for federal state
        url_segment = self.BUNDESLAND_MAPPING.get(federal_state)
        if not url_segment:
            raise SchoolHolidayApiError(f"Unknown federal state: {federal_state}")
        
        # Build API URL
        url = f"{self.BASE_URL}/{url_segment}/periods"
        params = {
            "start_date": f"{year}-01-01",
            "end_date": f"{year}-12-31"
        }
        
        logger.info(f"Fetching school holidays for {federal_state.value} ({year})")
        
        try:
            # Make API request
            data = await self._make_request(url, params)
            
            # Handle wrapped response (API v2.1 returns {data: [...], meta: ...})
            holidays_list = data
            if isinstance(data, dict) and "data" in data:
                holidays_list = data["data"]
            
            # Filter only school vacations
            school_holidays = [
                item for item in holidays_list
                if isinstance(item, dict) and item.get("is_school_vacation", False) and not item.get("is_public_holiday", False)
            ]
            
            # Transform to internal format
            transformed_holidays = []
            for holiday in school_holidays:
                transformed = self._transform_holiday_data(holiday, federal_state, year)
                if transformed:
                    transformed_holidays.append(transformed)
            
            self.session_stats["total_holidays_fetched"] += len(transformed_holidays)
            logger.info(f"Successfully fetched {len(transformed_holidays)} school holidays for {federal_state.value} ({year})")
            
            return transformed_holidays
            
        except Exception as e:
            logger.error(f"Failed to fetch school holidays for {federal_state.value} ({year}): {e}")
            raise
    
    async def fetch_bulk_holidays(self, years: List[int], federal_states: Optional[List[FederalState]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch school holidays for multiple years and federal states
        
        Args:
            years: List of years to fetch
            federal_states: List of federal states (default: all 16 states)
            
        Returns:
            Dictionary with keys like "BW_2025" and values as holiday lists
            
        Raises:
            SchoolHolidayApiError: If any API request fails
        """
        if federal_states is None:
            federal_states = list(FederalState)
        
        logger.info(f"Starting bulk fetch for {len(federal_states)} states and {len(years)} years")
        
        results = {}
        tasks = []
        
        # Create tasks for concurrent execution
        for state in federal_states:
            for year in years:
                task = self._fetch_with_key(state, year)
                tasks.append(task)
        
        # Execute all tasks concurrently with rate limiting
        semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        try:
            # Execute tasks in batches to respect rate limits
            batch_results = await asyncio.gather(*[limited_task(task) for task in tasks], return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Bulk fetch task failed: {result}")
                    continue
                
                key, holidays = result
                results[key] = holidays
            
            total_holidays = sum(len(holidays) for holidays in results.values())
            logger.info(f"Bulk fetch completed: {len(results)} successful requests, {total_holidays} total holidays")
            
            return results
            
        except Exception as e:
            logger.error(f"Bulk fetch failed: {e}")
            raise SchoolHolidayApiError(f"Bulk fetch failed: {e}")
    
    async def _fetch_with_key(self, federal_state: FederalState, year: int) -> tuple[str, List[Dict[str, Any]]]:
        """Helper method for bulk fetch with result key"""
        key = f"{federal_state.name}_{year}"
        holidays = await self.fetch_school_holidays(federal_state, year)
        return key, holidays
    
    def _transform_holiday_data(self, api_data: Dict[str, Any], federal_state: FederalState, year: int) -> Optional[Dict[str, Any]]:
        """
        Transform API response data to internal format
        
        Args:
            api_data: Raw API response data
            federal_state: Federal state for the holiday
            year: Year for the holiday
            
        Returns:
            Transformed holiday data or None if invalid
        """
        try:
            # Extract basic information
            name = api_data.get("name", "").strip()
            starts_on = api_data.get("starts_on")
            ends_on = api_data.get("ends_on")
            api_id = str(api_data.get("id", ""))
            
            if not all([name, starts_on, ends_on]):
                logger.warning(f"Incomplete holiday data: {api_data}")
                return None
            
            # Parse dates
            try:
                start_date = datetime.strptime(starts_on, "%Y-%m-%d").date()
                end_date = datetime.strptime(ends_on, "%Y-%m-%d").date()
            except ValueError as e:
                logger.warning(f"Invalid date format in holiday data: {e}")
                return None
            
            # Map vacation type
            vacation_type = self._map_vacation_type(name)
            if not vacation_type:
                logger.warning(f"Unknown vacation type for holiday: {name}")
                return None  # Skip unknown types instead of defaulting to SUMMER
            
            # Create transformed data
            transformed = {
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "federal_state": federal_state,
                "federal_state_code": federal_state.value,
                "school_vacation_type": vacation_type,
                "data_source": DataSource.MEHR_SCHULFERIEN_API,
                "api_id": api_id,
                "year": year,
                "notes": f"Imported from mehr-schulferien.de API on {datetime.now().strftime('%Y-%m-%d')}"
            }
            
            return transformed
            
        except Exception as e:
            logger.error(f"Failed to transform holiday data: {e}")
            return None
    
    def _map_vacation_type(self, vacation_name: str) -> Optional[SchoolVacationType]:
        """
        Map vacation name from API to internal SchoolVacationType
        
        Args:
            vacation_name: Vacation name from API
            
        Returns:
            Mapped SchoolVacationType or None
        """
        # Direct mapping
        if vacation_name in self.VACATION_TYPE_MAPPING:
            return self.VACATION_TYPE_MAPPING[vacation_name]
        
        # Fuzzy matching for variations
        vacation_lower = vacation_name.lower()
        
        if "winter" in vacation_lower:
            return SchoolVacationType.WINTER
        elif "oster" in vacation_lower:
            return SchoolVacationType.EASTER
        elif "pfingst" in vacation_lower:
            return SchoolVacationType.PENTECOST
        elif "sommer" in vacation_lower:
            return SchoolVacationType.SUMMER
        elif "herbst" in vacation_lower:
            return SchoolVacationType.AUTUMN
        elif "weihnacht" in vacation_lower:
            return SchoolVacationType.CHRISTMAS
        elif "frühjahr" in vacation_lower or "fasching" in vacation_lower:
            return SchoolVacationType.WINTER
        elif "himmelfahrt" in vacation_lower:
            return SchoolVacationType.PENTECOST
        elif "unterrichtsfrei" in vacation_lower:
            return None
        
        return None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current session
        
        Returns:
            Dictionary with session statistics
        """
        stats = self.session_stats.copy()
        stats["success_rate"] = (
            stats["successful_requests"] / stats["requests_made"] * 100
            if stats["requests_made"] > 0 else 0
        )
        return stats
    
    def reset_session_stats(self) -> None:
        """Reset session statistics"""
        self.session_stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retries_used": 0,
            "total_holidays_fetched": 0
        }
        logger.info("Session statistics reset")


# Convenience function for dependency injection
def get_school_holiday_api_client() -> SchoolHolidayApiClient:
    """
    Factory function for SchoolHolidayApiClient
    
    Returns:
        Configured SchoolHolidayApiClient instance
    """
    return SchoolHolidayApiClient(
        timeout=30,
        max_retries=3
    )
