#!/usr/bin/env python3
from test_data_generator import TestDataGenerator

gen = TestDataGenerator()
if gen.authenticate():
    employees = gen.get_all_employees()
    print(f'Total employees found: {len(employees)}')
    for i, emp in enumerate(employees[:3]):
        print(f'  {i+1}. {emp.get("first_name", "")} {emp.get("last_name", "")} (ID: {emp["id"]}, Active: {emp.get("active", "N/A")})')
else:
    print('Authentication failed')
