import random


def simulate_price_change(current_price: float) -> float:
    """
    Simulate realistic price changes:
    - Most of the time (90%): small fluctuation ±5%
    - Sometimes (10%): large drop to simulate a sale
    """
    if random.random() < 0.10:
        change_percent = random.uniform(-0.40, -0.20)  # 20%-40% drop
    else:
        change_percent = random.uniform(-0.05, 0.05)  # Natural fluctuation

    new_price = current_price * (1 + change_percent)

    # Ensure price doesn't go below 1
    return round(max(new_price, 1.0), 2)
