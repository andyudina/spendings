"""
Spendings related utils
"""

def aggregate_spendings_by_name(items):
    """
    Sum quantity for spendings with same name
    """
    result = {}
    for item in items:
        name = item['item'].lower()
        result[name] = result.get(
            name, 
            {
                'quantity': 0,
                'amount': 0
            })
        result[name]['quantity'] += 1
        result[name]['amount'] += item['amount']
    return result
