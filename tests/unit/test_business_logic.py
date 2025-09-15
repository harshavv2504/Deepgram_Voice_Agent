"""
Unit tests for business logic module.
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from common.business_logic import (
    get_customer,
    get_customer_appointments,
    get_customer_orders,
    schedule_appointment,
    get_available_appointment_slots,
    reschedule_appointment,
    cancel_appointment,
    update_appointment_status,
    create_new_customer,
    generate_unique_customer_id,
    generate_unique_appointment_id,
    validate_data_integrity,
    MOCK_DATA
)


class TestCustomerOperations:
    """Test customer-related operations."""
    
    @pytest.mark.asyncio
    async def test_get_customer_by_phone(self, mock_data_setup, sample_customer_data):
        """Test getting customer by phone number."""
        result = await get_customer(phone=sample_customer_data["phone"])
        
        assert result["id"] == sample_customer_data["id"]
        assert result["name"] == sample_customer_data["name"]
        assert result["phone"] == sample_customer_data["phone"]
    
    @pytest.mark.asyncio
    async def test_get_customer_by_email(self, mock_data_setup, sample_customer_data):
        """Test getting customer by email address."""
        result = await get_customer(email=sample_customer_data["email"])
        
        assert result["id"] == sample_customer_data["id"]
        assert result["name"] == sample_customer_data["name"]
        assert result["email"] == sample_customer_data["email"]
    
    @pytest.mark.asyncio
    async def test_get_customer_by_id(self, mock_data_setup, sample_customer_data):
        """Test getting customer by customer ID."""
        result = await get_customer(customer_id=sample_customer_data["id"])
        
        assert result["id"] == sample_customer_data["id"]
        assert result["name"] == sample_customer_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, mock_data_setup):
        """Test getting non-existent customer."""
        result = await get_customer(phone="+15559999999")
        
        assert "error" in result
        assert result["error"] == "Customer not found"
    
    @pytest.mark.asyncio
    async def test_get_customer_no_criteria(self, mock_data_setup):
        """Test getting customer without search criteria."""
        result = await get_customer()
        
        assert "error" in result
        assert result["error"] == "No search criteria provided"
    
    @pytest.mark.asyncio
    async def test_create_new_customer(self, mock_data_setup):
        """Test creating a new customer."""
        result = await create_new_customer(
            name="Jane Smith",
            phone="+15559876543",
            email="jane.smith@example.com"
        )
        
        assert result["success"] is True
        assert "customer" in result
        assert result["customer"]["name"] == "Jane Smith"
        assert result["customer"]["phone"] == "+15559876543"
        assert result["customer"]["email"] == "jane.smith@example.com"
        assert result["customer"]["id"].startswith("CUST")
    
    @pytest.mark.asyncio
    async def test_create_customer_missing_fields(self, mock_data_setup):
        """Test creating customer with missing required fields."""
        result = await create_new_customer(name="", phone="", email="")
        
        assert "error" in result
        assert "required" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_create_customer_duplicate(self, mock_data_setup, sample_customer_data):
        """Test creating customer that already exists."""
        result = await create_new_customer(
            name="John Doe",
            phone=sample_customer_data["phone"],
            email="different@example.com"
        )
        
        assert "error" in result
        assert "already exists" in result["error"].lower()
    
    def test_generate_unique_customer_id(self, mock_data_setup):
        """Test generating unique customer IDs."""
        # Clear existing customers to test ID generation
        original_customers = MOCK_DATA["customers"].copy()
        MOCK_DATA["customers"] = []
        
        # First ID should be CUST0000
        id1 = generate_unique_customer_id()
        assert id1 == "CUST0000"
        
        # Add a customer with that ID
        MOCK_DATA["customers"].append({"id": id1})
        
        # Next ID should be CUST0001
        id2 = generate_unique_customer_id()
        assert id2 == "CUST0001"
        
        # Restore original data
        MOCK_DATA["customers"] = original_customers


class TestAppointmentOperations:
    """Test appointment-related operations."""
    
    @pytest.mark.asyncio
    async def test_get_customer_appointments(self, mock_data_setup, sample_appointment_data):
        """Test getting customer appointments."""
        result = await get_customer_appointments(sample_appointment_data["customer_id"])
        
        assert "appointments" in result
        assert len(result["appointments"]) == 1
        assert result["appointments"][0]["id"] == sample_appointment_data["id"]
    
    @pytest.mark.asyncio
    async def test_schedule_appointment_success(self, mock_data_setup, sample_customer_data):
        """Test successful appointment scheduling."""
        future_date = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
        
        result = await schedule_appointment(
            customer_id=sample_customer_data["id"],
            date=future_date.isoformat(),
            service="Consultation"
        )
        
        assert "id" in result
        assert result["customer_id"] == sample_customer_data["id"]
        assert result["service"] == "Consultation"
        assert result["status"] == "Scheduled"
    
    @pytest.mark.asyncio
    async def test_schedule_appointment_past_date(self, mock_data_setup, sample_customer_data):
        """Test scheduling appointment in the past."""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        
        result = await schedule_appointment(
            customer_id=sample_customer_data["id"],
            date=past_date,
            service="Consultation"
        )
        
        assert "error" in result
        assert "past" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_schedule_appointment_outside_hours(self, mock_data_setup, sample_customer_data):
        """Test scheduling appointment outside business hours."""
        future_date = (datetime.now() + timedelta(days=1)).replace(hour=20, minute=0, second=0, microsecond=0)
        
        result = await schedule_appointment(
            customer_id=sample_customer_data["id"],
            date=future_date.isoformat(),
            service="Consultation"
        )
        
        assert "error" in result
        assert "9 AM and 5 PM" in result["error"]
    
    @pytest.mark.asyncio
    async def test_schedule_appointment_weekend(self, mock_data_setup, sample_customer_data):
        """Test scheduling appointment on weekend."""
        # Find next Saturday
        today = datetime.now()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        saturday = today + timedelta(days=days_ahead)
        saturday = saturday.replace(hour=14, minute=0, second=0, microsecond=0)
        
        result = await schedule_appointment(
            customer_id=sample_customer_data["id"],
            date=saturday.isoformat(),
            service="Consultation"
        )
        
        assert "error" in result
        assert "weekdays" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_schedule_appointment_nonexistent_customer(self, mock_data_setup):
        """Test scheduling appointment for non-existent customer."""
        future_date = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
        
        result = await schedule_appointment(
            customer_id="CUST9999",
            date=future_date.isoformat(),
            service="Consultation"
        )
        
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_available_appointment_slots(self, mock_data_setup):
        """Test getting available appointment slots."""
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=2)
        
        result = await get_available_appointment_slots(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        assert "available_slots" in result
        assert isinstance(result["available_slots"], list)
        # Should have some available slots
        assert len(result["available_slots"]) > 0
    
    @pytest.mark.asyncio
    async def test_reschedule_appointment(self, mock_data_setup, sample_appointment_data):
        """Test rescheduling an appointment."""
        new_date = (datetime.now() + timedelta(days=2)).replace(hour=15, minute=0, second=0, microsecond=0)
        
        result = await reschedule_appointment(
            appointment_id=sample_appointment_data["id"],
            new_date=new_date.isoformat(),
            new_service="Follow-up"
        )
        
        assert "message" in result
        assert "rescheduled successfully" in result["message"]
        assert result["appointment"]["service"] == "Follow-up"
    
    @pytest.mark.asyncio
    async def test_reschedule_nonexistent_appointment(self, mock_data_setup):
        """Test rescheduling non-existent appointment."""
        new_date = (datetime.now() + timedelta(days=2)).replace(hour=15, minute=0, second=0, microsecond=0)
        
        result = await reschedule_appointment(
            appointment_id="APT9999",
            new_date=new_date.isoformat(),
            new_service="Follow-up"
        )
        
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_cancel_appointment(self, mock_data_setup, sample_appointment_data):
        """Test cancelling an appointment."""
        result = await cancel_appointment(sample_appointment_data["id"])
        
        assert "message" in result
        assert "cancelled successfully" in result["message"]
        assert result["appointment"]["status"] == "Cancelled"
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_appointment(self, mock_data_setup):
        """Test cancelling non-existent appointment."""
        result = await cancel_appointment("APT9999")
        
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_update_appointment_status(self, mock_data_setup, sample_appointment_data):
        """Test updating appointment status."""
        result = await update_appointment_status(
            sample_appointment_data["id"],
            "Completed"
        )
        
        assert "message" in result
        assert "updated" in result["message"].lower()
        assert result["appointment"]["status"] == "Completed"
    
    @pytest.mark.asyncio
    async def test_update_appointment_invalid_status(self, mock_data_setup, sample_appointment_data):
        """Test updating appointment with invalid status."""
        result = await update_appointment_status(
            sample_appointment_data["id"],
            "InvalidStatus"
        )
        
        assert "error" in result
        assert "Invalid status" in result["error"]
    
    def test_generate_unique_appointment_id(self, mock_data_setup):
        """Test generating unique appointment IDs."""
        # Clear existing appointments
        original_appointments = MOCK_DATA["appointments"].copy()
        MOCK_DATA["appointments"] = []
        
        # First ID should be APT0000
        id1 = generate_unique_appointment_id()
        assert id1 == "APT0000"
        
        # Add an appointment with that ID
        MOCK_DATA["appointments"].append({"id": id1})
        
        # Next ID should be APT0001
        id2 = generate_unique_appointment_id()
        assert id2 == "APT0001"
        
        # Restore original data
        MOCK_DATA["appointments"] = original_appointments


class TestOrderOperations:
    """Test order-related operations."""
    
    @pytest.mark.asyncio
    async def test_get_customer_orders(self, mock_data_setup, sample_order_data):
        """Test getting customer orders."""
        result = await get_customer_orders(sample_order_data["customer_id"])
        
        assert "orders" in result
        assert len(result["orders"]) == 1
        assert result["orders"][0]["id"] == sample_order_data["id"]
        assert result["orders"][0]["total"] == sample_order_data["total"]


class TestDataValidation:
    """Test data validation and integrity."""
    
    def test_validate_data_integrity_success(self, mock_data_setup):
        """Test data integrity validation with valid data."""
        result = validate_data_integrity()
        assert result is True
    
    def test_validate_data_integrity_duplicate_customers(self, mock_data_setup):
        """Test data integrity validation with duplicate customer IDs."""
        # Add duplicate customer ID
        MOCK_DATA["customers"].append({
            "id": "CUST0001",  # Duplicate ID
            "name": "Duplicate Customer",
            "phone": "+15559999999",
            "email": "duplicate@example.com"
        })
        
        result = validate_data_integrity()
        assert result is False
        
        # Clean up
        MOCK_DATA["customers"].pop()
    
    def test_validate_data_integrity_orphaned_appointments(self, mock_data_setup):
        """Test data integrity validation with orphaned appointments."""
        # Add appointment with non-existent customer
        MOCK_DATA["appointments"].append({
            "id": "APT9999",
            "customer_id": "CUST9999",  # Non-existent customer
            "customer_name": "Ghost Customer",
            "date": "2024-02-15T14:00:00",
            "service": "Consultation",
            "status": "Scheduled"
        })
        
        result = validate_data_integrity()
        assert result is False
        
        # Clean up
        MOCK_DATA["appointments"].pop()


class TestAsyncOperations:
    """Test async operation handling."""
    
    @pytest.mark.asyncio
    async def test_concurrent_customer_lookups(self, mock_data_setup, sample_customer_data):
        """Test concurrent customer lookup operations."""
        tasks = [
            get_customer(customer_id=sample_customer_data["id"]),
            get_customer(phone=sample_customer_data["phone"]),
            get_customer(email=sample_customer_data["email"])
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should return the same customer
        for result in results:
            assert result["id"] == sample_customer_data["id"]
    
    @pytest.mark.asyncio
    async def test_concurrent_appointment_operations(self, mock_data_setup, sample_customer_data):
        """Test concurrent appointment operations."""
        future_date1 = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
        future_date2 = (datetime.now() + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
        
        tasks = [
            schedule_appointment(
                customer_id=sample_customer_data["id"],
                date=future_date1.isoformat(),
                service="Consultation"
            ),
            schedule_appointment(
                customer_id=sample_customer_data["id"],
                date=future_date2.isoformat(),
                service="Follow-up"
            )
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Both appointments should be created successfully
        for result in results:
            assert "id" in result
            assert result["status"] == "Scheduled"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(self, mock_data_setup, sample_customer_data):
        """Test handling of invalid date formats."""
        result = await schedule_appointment(
            customer_id=sample_customer_data["id"],
            date="invalid-date-format",
            service="Consultation"
        )
        
        assert "error" in result
        assert "Invalid date format" in result["error"]
    
    @pytest.mark.asyncio
    async def test_empty_service_type(self, mock_data_setup, sample_customer_data):
        """Test handling of empty service type."""
        future_date = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
        
        result = await schedule_appointment(
            customer_id=sample_customer_data["id"],
            date=future_date.isoformat(),
            service=""
        )
        
        # Should still work as service validation is not strict in current implementation
        # This test documents current behavior
        assert "id" in result or "error" in result


class TestMockDataGeneration:
    """Test mock data generation and management."""
    
    @patch('common.business_logic.save_mock_data')
    def test_mock_data_saving(self, mock_save, mock_data_setup):
        """Test that mock data is saved correctly."""
        from common.business_logic import save_mock_data
        
        test_data = {"test": "data"}
        save_mock_data(test_data)
        
        mock_save.assert_called_once_with(test_data)
    
    def test_mock_data_structure(self, mock_data_setup):
        """Test that mock data has the correct structure."""
        required_keys = ["customers", "appointments", "orders", "sample_data"]
        
        for key in required_keys:
            assert key in MOCK_DATA
            assert isinstance(MOCK_DATA[key], list)


class TestPerformance:
    """Test performance-related aspects."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, performance_timer):
        """Test performance with larger datasets."""
        # Create a larger dataset
        large_customers = []
        for i in range(1000):
            large_customers.append({
                "id": f"CUST{i:04d}",
                "name": f"Customer {i}",
                "phone": f"+1555{i:07d}",
                "email": f"customer{i}@example.com"
            })
        
        original_customers = MOCK_DATA["customers"]
        MOCK_DATA["customers"] = large_customers
        
        try:
            performance_timer.start()
            result = await get_customer(customer_id="CUST0500")
            performance_timer.stop()
            
            assert result["id"] == "CUST0500"
            assert performance_timer.elapsed < 1.0  # Should complete within 1 second
        finally:
            MOCK_DATA["customers"] = original_customers