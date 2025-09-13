ARTIFICIAL_DELAY = {
    "database": 0.0,
    "external_api": 0.0, # Not in use in this reference implementation but left as an example for simulating different delays
    "heavy_computation": 0.0 # Not in use in this reference implementation but left as an example for simulating different delays
}


# Mock data settings
MOCK_DATA_SIZE = {
    "customers": 1000,
    "appointments": 500,
    "orders": 2000
}

# Database settings (if using SQLite)
# Not in use in this reference implementation but left as an example for how to potentially integrate with a DB
DATABASE_CONFIG = {
    "path": "business_data.db",
    "enable": False  # Set to True to use actual SQLite instead of mock data
} 