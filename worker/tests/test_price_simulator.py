from price_simulator import simulate_price_change


def test_simulate_returns_float():
    """Verify that simulate_price_change returns a float value"""
    result = simulate_price_change(100.0)

    assert isinstance(result, float), "Result should be a float"
    assert result > 0, "Price should be positive"

def test_simulate_minimum_price_is_one():
    """Verify that simulated prices never drop below 1.0"""
    low_price = 1.0

    # Test multiple iterations to ensure minimum price constraint
    for _ in range(100):
        new_price = simulate_price_change(low_price)

        assert new_price >= 1.0, f"Price dropped below minimum: {new_price}"

def test_simulate_returns_two_decimals():
    """Verify that prices are rounded to exactly 2 decimal places"""
    result = simulate_price_change(99.9999999)

    # Check that result matches its rounded version
    assert result == round(result, 2), "Price should have max 2 decimal places"

def test_simulate_stays_in_realistic_range():
    """Verify that simulated price changes stay within realistic market bounds"""
    current_price = 100.0

    # Test multiple iterations for consistency
    for _ in range(100):
        new_price = simulate_price_change(current_price)

        # Define realistic price change limits based on simulation rules
        min_allowed = current_price * 0.60  # Maximum 40% drop
        max_allowed = current_price * 1.05  # Maximum 5% increase

        assert new_price >= min_allowed, f"Price change exceeded minimum bound: {new_price}"
        assert new_price <= max_allowed, f"Price change exceeded maximum bound: {new_price}"
