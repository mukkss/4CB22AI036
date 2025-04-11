from django.shortcuts import render
import requests
from django.http import JsonResponse
from collections import deque
from django.conf import settings  # For ACCESS_TOKEN

# Set sliding window size
WINDOW_SIZE = 10

# Store the current window state
number_window = deque(maxlen=WINDOW_SIZE)

# Mapping number type to external API endpoints
TYPE_TO_URL = {
    'p': 'http://20.244.56.144/evaluation-service/primes',
    'f': 'http://20.244.56.144/evaluation-service/fibo',
    'e': 'http://20.244.56.144/evaluation-service/even',
    'r': 'http://20.244.56.144/evaluation-service/rand',
}

def number_handler(request, number_type):
    if number_type not in TYPE_TO_URL:
        print(f"Invalid number type requested: {number_type}")
        return JsonResponse({"error": "Invalid number type"}, status=400)

    prev_state = list(number_window)
    new_numbers = []

    url = TYPE_TO_URL[number_type]
    headers = {
        "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
    }

    print(f"\nRequesting numbers of type '{number_type}' from: {url}")
    print(f"Token start: {settings.ACCESS_TOKEN[:10]}...")

    try:
        response = requests.get(url, headers=headers, timeout=1)
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            new_numbers = data.get("numbers", [])
            print(f"Received numbers: {new_numbers}")
        else:
            print(f"Failed to fetch numbers. Status: {response.status_code}, Body: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request exception occurred: {e}")

    # Add only new unique numbers until the window is full
    added_count = 0
    for num in new_numbers:
        if num not in number_window:
            number_window.append(num)
            added_count += 1
            if len(number_window) == WINDOW_SIZE:
                break

    curr_state = list(number_window)
    avg = round(sum(curr_state) / len(curr_state), 2) if curr_state else 0.0

    return JsonResponse({
        "windowPrevState": prev_state,
        "windowCurrState": curr_state,
        "numbers": new_numbers,
        "avg": avg
    })
