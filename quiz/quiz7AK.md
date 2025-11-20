# Quiz 7A - Answer Key


**Question 1:** What does CRUD stand for?

**Answer:**

CRUD stands for:

1. **C - Create**
2. **R - Read**
3. **U - Update**
4. **D - Delete**


**Question 3:** Write a single test function called `test_calculate_discount` that tests the `calculate_discount` function and logs successful results

**Answer:**

```python
def test_calculate_discount():
    result1 = calculate_discount(100, 10)
    assert result1 == 90.0
    logger.info(f"Test passed: {100}, {10}, {result1}")
    
    result2 = calculate_discount(50, 20)
    assert result2 == 40.0
    logger.info(f"Test passed: {50}, {20}, {result2}")
```


**Question 3:** Write a single integration test function called `test_discount_edge_cases` that tests edge cases and logs successful results

**Answer:**

```python
def test_discount_edge_cases():
    # Test that applying zero discounts (no arguments) returns the original price
    result1 = apply_multiple_discounts(100)
    assert result1 == 100.0
    logger.info(f"Test passed: {100}, {0}, {result1}")
    
    # Test that applying a 0% discount produces the same result as applying no discount
    result2 = apply_multiple_discounts(100, 0)
    assert result2 == 100.0
    logger.info(f"Test passed: {100}, {0}, {result2}")
    
    # Test that applying a 100% discount results in a final price of 0.0
    result3 = apply_multiple_discounts(100, 100)
    assert result3 == 0.0
    logger.info(f"Test passed: {100}, {100}, {result3}")
```


**Question 4:** Explain why the `site/` directory should not be included in a git repository

**Answer:**

The `site/` directory should not be included in a git repository because it is generated automatically by MkDocs from source files and can be regenerated, so there's no need to track it in version control.
