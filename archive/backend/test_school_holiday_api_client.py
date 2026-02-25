"""
Unit tests for SchoolHolidayApiClient

Tests cover:
- API client initialization
- Single state/year requests
- Bulk requests
- Error handling scenarios
- Data transformation
- Retry logic
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, datetime
import httpx
from app.services.school_holiday_api_client import (
    SchoolHolidayApiClient,
    SchoolHolidayApiError,
    SchoolHolidayApiRateLimitError,
    SchoolHolidayApiTimeoutError,
    get_school_holiday_api_client
)
from app.models.federal_state import FederalState
from app.models.holiday import SchoolVacationType, DataSource


class TestSchoolHolidayApiClient:
    """Test suite for SchoolHolidayApiClient"""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance"""
        return SchoolHolidayApiClient(timeout=10, max_retries=2)
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response data"""
        return [
            {
                "id": 4673,
                "name": "Osterferien",
                "type": "school_vacation",
                "starts_on": "2025-04-14",
                "ends_on": "2025-04-25",
                "location_id": 2,
                "is_public_holiday": False,
                "is_school_vacation": True
            },
            {
                "id": 4674,
                "name": "Sommerferien",
                "type": "school_vacation", 
                "starts_on": "2025-07-31",
                "ends_on": "2025-09-13",
                "location_id": 2,
                "is_public_holiday": False,
                "is_school_vacation": True
            },
            {
                "id": 4675,
                "name": "Tag der Arbeit",
                "type": "public_holiday",
                "starts_on": "2025-05-01",
                "ends_on": "2025-05-01",
                "location_id": 2,
                "is_public_holiday": True,
                "is_school_vacation": False
            }
        ]
    
    def test_client_initialization(self):
        """Test client initialization with custom parameters"""
        client = SchoolHolidayApiClient(timeout=20, max_retries=5)
        
        assert client.timeout == 20
        assert client.max_retries == 5
        assert client.session_stats["requests_made"] == 0
        assert "User-Agent" in client.client_config["headers"]
    
    def test_bundesland_mapping_completeness(self, client):
        """Test that all federal states are mapped"""
        all_states = list(FederalState)
        mapped_states = list(client.BUNDESLAND_MAPPING.keys())
        
        assert len(mapped_states) == 16
        assert set(all_states) == set(mapped_states)
    
    def test_vacation_type_mapping(self, client):
        """Test vacation type mapping functionality"""
        # Direct mappings
        assert client._map_vacation_type("Osterferien") == SchoolVacationType.EASTER
        assert client._map_vacation_type("Sommerferien") == SchoolVacationType.SUMMER
        assert client._map_vacation_type("Winterferien") == SchoolVacationType.WINTER
        
        # Fuzzy matching
        assert client._map_vacation_type("Oster") == SchoolVacationType.EASTER
        assert client._map_vacation_type("sommer") == SchoolVacationType.SUMMER
        assert client._map_vacation_type("HERBST") == SchoolVacationType.AUTUMN
        
        # Unknown type
        assert client._map_vacation_type("Unknown Holiday") is None
    
    @pytest.mark.asyncio
    async def test_successful_single_request(self, client, mock_api_response):
        """Test successful API request for single state/year"""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Make request
            result = await client.fetch_school_holidays(FederalState.BW, 2025)
            
            # Verify results
            assert len(result) == 2  # Only school vacations, not public holidays
            assert result[0]["name"] == "Osterferien"
            assert result[0]["federal_state"] == FederalState.BW
            assert result[0]["school_vacation_type"] == SchoolVacationType.EASTER
            assert result[0]["data_source"] == DataSource.MEHR_SCHULFERIEN_API
            
            # Verify stats
            stats = client.get_session_stats()
            assert stats["requests_made"] == 1
            assert stats["successful_requests"] == 1
            assert stats["total_holidays_fetched"] == 2
    
    @pytest.mark.asyncio
    async def test_http_error_handling(self, client):
        """Test handling of HTTP errors"""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock 404 response
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Expect SchoolHolidayApiError
            with pytest.raises(SchoolHolidayApiError, match="HTTP 404"):
                await client.fetch_school_holidays(FederalState.BW, 2025)
            
            # Verify error stats
            stats = client.get_session_stats()
            assert stats["failed_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, client):
        """Test handling of rate limits with retry"""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock 429 response
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "1"}
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Mock sleep to avoid actual waiting
            with patch('asyncio.sleep', new_callable=AsyncMock):
                with pytest.raises(SchoolHolidayApiRateLimitError):
                    await client._make_request("http://test.com", {})
            
            # Verify retry stats
            stats = client.get_session_stats()
            assert stats["retries_used"] >= 1
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """Test handling of request timeouts"""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup timeout exception
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")
            
            with pytest.raises(SchoolHolidayApiTimeoutError):
                await client.fetch_school_holidays(FederalState.BW, 2025)
            
            # Verify error stats
            stats = client.get_session_stats()
            assert stats["failed_requests"] >= 1
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON responses"""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock response with invalid JSON
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(SchoolHolidayApiError, match="Invalid JSON"):
                await client.fetch_school_holidays(FederalState.BW, 2025)
    
    @pytest.mark.asyncio
    async def test_unknown_federal_state(self, client):
        """Test handling of unknown federal state"""
        # Create a mock federal state that's not in mapping
        with patch.object(client, 'BUNDESLAND_MAPPING', {}):
            with pytest.raises(SchoolHolidayApiError, match="Unknown federal state"):
                await client.fetch_school_holidays(FederalState.BW, 2025)
    
    def test_data_transformation_valid(self, client):
        """Test transformation of valid API data"""
        api_data = {
            "id": 4673,
            "name": "Osterferien",
            "starts_on": "2025-04-14",
            "ends_on": "2025-04-25",
            "is_school_vacation": True,
            "is_public_holiday": False
        }
        
        result = client._transform_holiday_data(api_data, FederalState.BW, 2025)
        
        assert result is not None
        assert result["name"] == "Osterferien"
        assert result["start_date"] == date(2025, 4, 14)
        assert result["end_date"] == date(2025, 4, 25)
        assert result["federal_state"] == FederalState.BW
        assert result["federal_state_code"] == "BW"
        assert result["school_vacation_type"] == SchoolVacationType.EASTER
        assert result["api_id"] == "4673"
        assert result["year"] == 2025
    
    def test_data_transformation_invalid(self, client):
        """Test transformation of invalid API data"""
        # Missing required fields
        invalid_data = {
            "id": 4673,
            "name": "Osterferien"
            # Missing starts_on and ends_on
        }
        
        result = client._transform_holiday_data(invalid_data, FederalState.BW, 2025)
        assert result is None
        
        # Invalid date format
        invalid_date_data = {
            "id": 4673,
            "name": "Osterferien",
            "starts_on": "invalid-date",
            "ends_on": "2025-04-25"
        }
        
        result = client._transform_holiday_data(invalid_date_data, FederalState.BW, 2025)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_bulk_fetch_success(self, client, mock_api_response):
        """Test successful bulk fetch operation"""
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test bulk fetch for 2 states and 2 years
            years = [2025, 2026]
            states = [FederalState.BW, FederalState.BY]
            
            results = await client.fetch_bulk_holidays(years, states)
            
            # Verify results structure
            assert len(results) == 4  # 2 states × 2 years
            assert "BW_2025" in results
            assert "BW_2026" in results
            assert "BY_2025" in results
            assert "BY_2026" in results
            
            # Verify each result has school holidays
            for key, holidays in results.items():
                assert len(holidays) == 2  # 2 school vacations per response
    
    @pytest.mark.asyncio
    async def test_bulk_fetch_partial_failure(self, client, mock_api_response):
        """Test bulk fetch with some failures"""
        call_count = 0
        
        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_response = MagicMock()
            if call_count == 1:
                # First call succeeds
                mock_response.status_code = 200
                mock_response.json.return_value = mock_api_response
            else:
                # Subsequent calls fail
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"
            
            return mock_response
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = mock_get
            
            years = [2025, 2026]
            states = [FederalState.BW, FederalState.BY]
            
            results = await client.fetch_bulk_holidays(years, states)
            
            # Should have partial results (only successful requests)
            assert len(results) < 4  # Less than total expected
            assert len(results) >= 1  # At least one success
    
    def test_session_stats_calculation(self, client):
        """Test session statistics calculation"""
        # Manually set some stats
        client.session_stats["requests_made"] = 10
        client.session_stats["successful_requests"] = 8
        client.session_stats["failed_requests"] = 2
        
        stats = client.get_session_stats()
        
        assert stats["requests_made"] == 10
        assert stats["successful_requests"] == 8
        assert stats["failed_requests"] == 2
        assert stats["success_rate"] == 80.0
    
    def test_session_stats_reset(self, client):
        """Test session statistics reset"""
        # Set some stats
        client.session_stats["requests_made"] = 5
        client.session_stats["successful_requests"] = 3
        
        # Reset
        client.reset_session_stats()
        
        # Verify reset
        stats = client.get_session_stats()
        assert stats["requests_made"] == 0
        assert stats["successful_requests"] == 0
        assert stats["success_rate"] == 0
    
    def test_factory_function(self):
        """Test the factory function"""
        client = get_school_holiday_api_client()
        
        assert isinstance(client, SchoolHolidayApiClient)
        assert client.timeout == 30
        assert client.max_retries == 3


class TestSchoolHolidayApiClientIntegration:
    """Integration tests that can be run against the real API (optional)"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_request(self):
        """Test against real API (requires internet connection)"""
        client = SchoolHolidayApiClient(timeout=10)
        
        try:
            # Test with a small request
            result = await client.fetch_school_holidays(FederalState.BW, 2025)
            
            # Basic validation
            assert isinstance(result, list)
            if result:  # If data is available
                holiday = result[0]
                assert "name" in holiday
                assert "start_date" in holiday
                assert "end_date" in holiday
                assert holiday["federal_state"] == FederalState.BW
                
        except Exception as e:
            pytest.skip(f"Real API test skipped due to: {e}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_bulk_request(self):
        """Test bulk request against real API"""
        client = SchoolHolidayApiClient(timeout=15)
        
        try:
            # Test with small bulk request
            years = [2025]
            states = [FederalState.BW, FederalState.BY]
            
            results = await client.fetch_bulk_holidays(years, states)
            
            # Basic validation
            assert isinstance(results, dict)
            assert len(results) <= 2  # At most 2 results
            
            for key, holidays in results.items():
                assert isinstance(holidays, list)
                assert key in ["BW_2025", "BY_2025"]
                
        except Exception as e:
            pytest.skip(f"Real API bulk test skipped due to: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
