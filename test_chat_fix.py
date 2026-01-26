#!/usr/bin/env python3
"""
Test to see if Groq API is actually working
"""
from chat.nur_chat import NurChat

# Test with Groq enabled
chat = NurChat({'use_groq': True})

# Test a query that should use Groq
print("Testing Groq API...")
response = chat.respond("Explain the 200 EMA trading strategy in simple terms")
print(f"\nResponse: {response}")

# Test another query
print("\n\nTesting another query...")
response2 = chat.respond("What is risk management in trading?")
print(f"\nResponse: {response2}")
