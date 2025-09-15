"""
Unit tests for agent functions module.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from common.agent_functions import (
    find_customer,
    get_appointments,
    get_orders,
    create_appointment,
    check_availability,
    reschedule_appointment_func,
    cancel_appointment_func,
    update_appointment_status_func,
    create_customer_account,
    search_knowledge_base,
    get_knowledge_base_topics,
    get_knowledge_base_entry,
    agent_filler,
    end_call,
    FUNCTION_DEFINITIONS,
    FUNCTION_MAP
)


class TestCustomerFunctions:
    """Test customer-related agent functions."""
    
    @pytest.mark.asyncio
    async def test_find_customer_by_phone(self, mock_data_setup, sample_customer_data):
        """Test finding customer by phone number."""
        result = await find_customer({"phone": sample_customer_data["phone"]})
        
        assert result["id"] == sample_customer_data["id"]
        assert result["name"] == sample_customer_data["name"]
    
    @pytest.mark.asyncio
    async def test_find_customer_by_email(self, mock_data_setup, sample_customer_data):
        """Test finding customer by email."""
        result = await find_customer({"email": sample_customer_data["email"]})
        
        assert result["id"] == sample_customer_data["id"]
        assert result["email"] == sample_customer_data["email"]
    
    @pytest.mark.asyncio
    async def test_find_customer_by_id(self, mock_data_setup, sample_customer_data):
        """Test finding customer by ID."""
        result = await find_customer({"customer_id": sample_customer_data["id"]})
        
        assert result["id"] == sample_customer_data["id"]
    
    @pytest.mark.asyncio
    async def test_find_customer_not_found(self, mock_data_setup):
        """Test finding non-existent customer."""
        result = await find_customer({"phone": "+15559999999"})
        
        assert "error" in result
        assert result["error"] == "Customer not found"
    
    @pytest.mark.asyncio
    async def test_create_customer_account_success(self, mock_data_setup):
        """Test successful customer account creation."""
        params = {
            "name": "Jane Smith",
            "phone": "+15559876543",
            "email": "jane.smith@example.com"
        }
        
        result = await create_customer_account(params)
        
        assert result["success"] is True
        assert "customer" in result
        assert result["customer"]["name"] == "Jane Smith"
    
    @pytest.mark.asyncio
    async def test_create_customer_account_missing_name(self, mock_data_setup):
        """Test customer account creation with missing name."""
        params = {
            "name": "",
            "phone": "+15559876543",
            "email": "jane.smith@example.com"
        }
        
        result = await create_customer_account(params)
        
        assert "error" in result
        assert "name is required" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_create_customer_account_invalid_phone(self, mock_data_setup):
        """Test customer account creation with invalid phone."""
        params = {
            "name": "Jane Smith",
            "phone": "invalid-phone",
            "email": "jane.smith@example.com"
        }
        
        result = await create_customer_account(params)
        
        assert "error" in result
        assert "international format" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_create_customer_account_invalid_email(self, mock_data_setup):
        """Test customer account creation with invalid email."""
        params = {
            "name": "Jane Smith",
            "phone": "+15559876543",
            "email": "invalid-email"
        }
        
        result = await create_customer_account(params)
        
        assert "error" in result
        assert "valid email" in result["error"].lower()


class TestAppointmentFunctions:
    """Test appointment-related agent functions."""
    
    @pytest.mark.asyncio
    async def test_get_appointments_success(self, mock_data_setup, sample_appointment_data):
        """Test getting customer appointments."""
        result = await get_appointments({"customer_id": sample_appointment_data["customer_id"]})
        
        assert "appointments" in result
        assert len(result["appointments"]) == 1
        assert result["appointments"][0]["id"] == sample_appointment_data["id"]
    
    @pytest.mark.asyncio
    async def test_get_appointments_missing_customer_id(self, mock_data_setup):
        """Test getting appointments without customer ID."""
        result = await get_appointments({})
        
        assert "error" in result
        assert "customer_id is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_appointment_success(self, mock_data_setup, sample_customer_data):
        """Test successful appointment creation."""
        from datetime import datetime, timedelta
        
        future_date = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
        
        params = {
            "customer_id": sample_customer_data["id"],
            "date": future_date.isoformat(),
            "service": "Consultation"
        }
        
        result = await create_appointment(params)
        
        assert "id" in result
        assert result["customer_id"] == sample_customer_data["id"]
        assert result["service"] == "Consultation"
    
    @pytest.mark.asyncio
    async def test_create_appointment_missing_params(self, mock_data_setup):
        """Test appointment creation with missing parameters."""
        result = await create_appointment({"customer_id": "CUST0001"})
        
        assert "error" in result
        assert "required" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_check_availability_success(self, mock_data_setup):
        """Test checking appointment availability."""
        from datetime import datetime, timedelta
        
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        params = {"start_date": start_date.isoformat()}
        result = await check_availability(params)
        
        assert "available_slots" in result
        assert isinstance(result["available_slots"], list)
    
    @pytest.mark.asyncio
    async def test_check_availability_missing_start_date(self, mock_data_setup):
        """Test checking availability without start date."""
        result = await check_availability({})
        
        assert "error" in result
        assert "start_date is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_reschedule_appointment_success(self, mock_data_setup, sample_appointment_data):
        """Test successful appointment rescheduling."""
        from datetime import datetime, timedelta
        
        new_date = (datetime.now() + timedelta(days=2)).replace(hour=15, minute=0, second=0, microsecond=0)
        
        params = {
            "appointment_id": sample_appointment_data["id"],
            "new_date": new_date.isoformat(),
            "new_service": "Follow-up"
        }
        
        result = await reschedule_appointment_func(params)
        
        assert "message" in result
        assert "rescheduled successfully" in result["message"]
    
    @pytest.mark.asyncio
    async def test_cancel_appointment_success(self, mock_data_setup, sample_appointment_data):
        """Test successful appointment cancellation."""
        params = {"appointment_id": sample_appointment_data["id"]}
        
        result = await cancel_appointment_func(params)
        
        assert "message" in result
        assert "cancelled successfully" in result["message"]
    
    @pytest.mark.asyncio
    async def test_update_appointment_status_success(self, mock_data_setup, sample_appointment_data):
        """Test successful appointment status update."""
        params = {
            "appointment_id": sample_appointment_data["id"],
            "new_status": "Completed"
        }
        
        result = await update_appointment_status_func(params)
        
        assert "message" in result
        assert "updated" in result["message"].lower()


class TestOrderFunctions:
    """Test order-related agent functions."""
    
    @pytest.mark.asyncio
    async def test_get_orders_success(self, mock_data_setup, sample_order_data):
        """Test getting customer orders."""
        result = await get_orders({"customer_id": sample_order_data["customer_id"]})
        
        assert "orders" in result
        assert len(result["orders"]) == 1
        assert result["orders"][0]["id"] == sample_order_data["id"]
    
    @pytest.mark.asyncio
    async def test_get_orders_missing_customer_id(self, mock_data_setup):
        """Test getting orders without customer ID."""
        result = await get_orders({})
        
        assert "error" in result
        assert "customer_id is required" in result["error"]


class TestKnowledgeBaseFunctions:
    """Test knowledge base-related agent functions."""
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_success(self, knowledge_base):
        """Test successful knowledge base search."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await search_knowledge_base({"query": "test"})
            
            assert result["found"] is True
            assert "title" in result
            assert "content" in result
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_no_results(self, knowledge_base):
        """Test knowledge base search with no results."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await search_knowledge_base({"query": "nonexistent"})
            
            assert result["found"] is False
            assert "message" in result
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_missing_query(self, knowledge_base):
        """Test knowledge base search without query."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await search_knowledge_base({})
            
            assert "error" in result
            assert "query is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_unavailable(self):
        """Test knowledge base search when unavailable."""
        with patch('common.agent_functions.mdx_kb', None):
            result = await search_knowledge_base({"query": "test"})
            
            assert "error" in result
            assert "not available" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_knowledge_base_topics_success(self, knowledge_base):
        """Test getting knowledge base topics."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await get_knowledge_base_topics({})
            
            assert "topics" in result
            assert isinstance(result["topics"], list)
    
    @pytest.mark.asyncio
    async def test_get_knowledge_base_entry_by_topic(self, knowledge_base):
        """Test getting knowledge base entry by topic."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await get_knowledge_base_entry({"topic": "Testing"})
            
            assert result["found"] is True
            assert "title" in result
            assert "content" in result
    
    @pytest.mark.asyncio
    async def test_get_knowledge_base_entry_by_title(self, knowledge_base):
        """Test getting knowledge base entry by title."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await get_knowledge_base_entry({"title": "Test Entry"})
            
            assert result["found"] is True
            assert result["title"] == "Test Entry"
    
    @pytest.mark.asyncio
    async def test_get_knowledge_base_entry_missing_params(self, knowledge_base):
        """Test getting knowledge base entry without parameters."""
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            result = await get_knowledge_base_entry({})
            
            assert "error" in result
            assert "required" in result["error"].lower()


class TestUtilityFunctions:
    """Test utility agent functions."""
    
    @pytest.mark.asyncio
    async def test_agent_filler(self, mock_websocket):
        """Test agent filler function."""
        params = {"message_type": "lookup"}
        
        result = await agent_filler(mock_websocket, params)
        
        assert "function_response" in result
        assert "inject_message" in result
        assert result["function_response"]["status"] == "queued"
    
    @pytest.mark.asyncio
    async def test_end_call(self, mock_websocket):
        """Test end call function."""
        params = {"farewell_type": "thanks"}
        
        result = await end_call(mock_websocket, params)
        
        assert "function_response" in result
        assert "inject_message" in result
        assert "close_message" in result
        assert result["function_response"]["status"] == "closing"


class TestFunctionDefinitions:
    """Test function definitions and mappings."""
    
    def test_function_definitions_structure(self):
        """Test that function definitions have correct structure."""
        for func_def in FUNCTION_DEFINITIONS:
            assert "name" in func_def
            assert "description" in func_def
            assert "parameters" in func_def
            
            # Check parameters structure
            params = func_def["parameters"]
            assert "type" in params
            assert params["type"] == "object"
            assert "properties" in params
    
    def test_function_map_completeness(self):
        """Test that all defined functions are mapped."""
        defined_functions = {func_def["name"] for func_def in FUNCTION_DEFINITIONS}
        mapped_functions = set(FUNCTION_MAP.keys())
        
        assert defined_functions == mapped_functions
    
    def test_function_map_callability(self):
        """Test that all mapped functions are callable."""
        for func_name, func in FUNCTION_MAP.items():
            assert callable(func), f"Function {func_name} is not callable"
    
    def test_required_functions_present(self):
        """Test that all required functions are present."""
        required_functions = {
            "find_customer",
            "get_appointments",
            "get_orders",
            "create_appointment",
            "check_availability",
            "agent_filler",
            "end_call",
            "search_knowledge_base",
            "create_customer_account"
        }
        
        mapped_functions = set(FUNCTION_MAP.keys())
        
        for required_func in required_functions:
            assert required_func in mapped_functions, f"Required function {required_func} not found"


class TestParameterValidation:
    """Test parameter validation in agent functions."""
    
    @pytest.mark.asyncio
    async def test_find_customer_parameter_handling(self, mock_data_setup):
        """Test find_customer parameter handling."""
        # Test with None values
        result = await find_customer({"phone": None, "email": None, "customer_id": None})
        assert "error" in result
        
        # Test with empty strings
        result = await find_customer({"phone": "", "email": "", "customer_id": ""})
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_create_appointment_parameter_validation(self, mock_data_setup):
        """Test create_appointment parameter validation."""
        # Missing all parameters
        result = await create_appointment({})
        assert "error" in result
        
        # Missing some parameters
        result = await create_appointment({"customer_id": "CUST0001"})
        assert "error" in result
        
        # Invalid date format
        result = await create_appointment({
            "customer_id": "CUST0001",
            "date": "invalid-date",
            "service": "Consultation"
        })
        assert "error" in result


class TestErrorHandling:
    """Test error handling in agent functions."""
    
    @pytest.mark.asyncio
    async def test_function_exception_handling(self, mock_data_setup):
        """Test that functions handle exceptions gracefully."""
        with patch('common.business_logic.get_customer', side_effect=Exception("Test error")):
            result = await find_customer({"customer_id": "CUST0001"})
            
            # Should not raise exception, should return error
            assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_knowledge_base_exception_handling(self):
        """Test knowledge base function exception handling."""
        mock_kb = MagicMock()
        mock_kb.search_knowledge_base.side_effect = Exception("KB Error")
        
        with patch('common.agent_functions.mdx_kb', mock_kb):
            result = await search_knowledge_base({"query": "test"})
            
            assert "error" in result
            assert "Error searching knowledge base" in result["error"]


class TestAsyncBehavior:
    """Test async behavior of agent functions."""
    
    @pytest.mark.asyncio
    async def test_concurrent_function_calls(self, mock_data_setup, sample_customer_data):
        """Test concurrent execution of agent functions."""
        import asyncio
        
        tasks = [
            find_customer({"customer_id": sample_customer_data["id"]}),
            get_appointments({"customer_id": sample_customer_data["id"]}),
            get_orders({"customer_id": sample_customer_data["id"]})
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 3
        assert all(isinstance(result, dict) for result in results)
    
    @pytest.mark.asyncio
    async def test_function_timeout_behavior(self, mock_data_setup):
        """Test function behavior under timeout conditions."""
        # This test would require more complex mocking to simulate timeouts
        # For now, we just test that functions complete in reasonable time
        import time
        
        start_time = time.time()
        result = await find_customer({"customer_id": "CUST0001"})
        end_time = time.time()
        
        # Should complete within 5 seconds
        assert end_time - start_time < 5.0
        assert isinstance(result, dict)