from django.shortcuts import render
import requests
import time
from django.http import JsonResponse
from collections import deque
from django.conf import settings  # <-- To get token from settings

# Set a window size
WINDOW_SIZE = 10

# Dictionary to store window state
number_window = deque(maxlen=WINDOW_SIZE)

# Mapping type to third-party URLs
TYPE_TO_URL = {
    'p': 'http://20.244.56.144/evaluation-service/primes',
    'f': 'http://20.244.56.144/evaluation-service/fibo',
    'e': 'http://20.244.56.144/evaluation-service/even',
    'r': 'http://20.244.56.144/evaluation-service/rand',
}

def number_handler(request, number_type):
    if number_type not in TYPE_TO_URL:
        print(f"Invalid type requested: {number_type}")
        return JsonResponse({"error": "Invalid number type"}, status=400)

    prev_state = list(number_window)
    new_numbers = []

    url = TYPE_TO_URL[number_type]
    headers = {
        "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
    }

    print(f"\nRequesting {number_type} numbers from: {url}")
    print(f"Using token: {settings.ACCESS_TOKEN[:10]}...")  # Show only start of token for safety

    try:
        response = requests.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            print(f"Raw Response: {response.text}")
            data = response.json()
            new_numbers = data.get("numbers", [])
            print(f"Parsed Numbers: {new_numbers}")
        else:
            print("Failed to fetch numbers:", response.status_code, response.text)

    except requests.exceptions.RequestException as e:
        print("Request exception occurred:", e)

    # Add new unique numbers
    for num in new_numbers:
        if num not in number_window:
            number_window.append(num)

    curr_state = list(number_window)
    avg = round(sum(curr_state) / len(curr_state), 2) if curr_state else 0.0


    return JsonResponse({
        "windowPrevState": prev_state,
        "windowCurrState": curr_state,
        "numbers": new_numbers,
        "avg": avg
    })
