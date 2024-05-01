employees = [
    { 'id': 1, 'name': 'Ashley' },
    { 'id': 2, 'name': 'Kate' },
    { 'id': 3, 'name': 'Joe' }
]

test_counter = 0

client_data = {
    "Doug": {
        "transactions": [
            {
                "date": "2024-04-01",
                "merchant": "Fashion Trends",
                "amount": 45.99,
                "category": "Clothing",
                "account": "Credit Card - Visa"
            },
            {
                "date": "2024-04-03",
                "merchant": "Tasty Bites Restaurant",
                "amount": 30.25,
                "category": "Dining Out",
                "account": "Credit Card - Mastercard"
            },
            {
                "date": "2024-04-10",
                "merchant": "Super Savers Market",
                "amount": 120.80,
                "category": "Groceries",
                "account": "Credit Card - American Express"
            },
            {
                "date": "2024-04-12",
                "merchant": "FootWear Express",
                "amount": 89.99,
                "category": "Clothing",
                "account": "Credit Card - Visa"
            },
            {
                "date": "2024-04-18",
                "merchant": "Outdoor Gear Emporium",
                "amount": 120.50,
                "category": "Clothing",
                "account": "Credit Card - American Express"
            },
            {
                "date": "2024-04-22",
                "merchant": "Tech Emporium",
                "amount": 300.00,
                "category": "Gas Station",
                "account": "Credit Card - Visa"
            },
            {
                "date": "2024-04-29",
                "merchant": "Gas Station",
                "amount": 45.00,
                "category": "Gas Station",
                "account": "Debit Card - Checking"
            },
            {
                "date": "2024-04-30",
                "merchant": "Bookstore",
                "amount": 65.00,
                "category": "Groceries",
                "account": "Credit Card - Visa"
            },
            {
                "date": "2024-05-01",
                "merchant": "Pharmacy",
                "amount": 20.50,
                "category": "Gas Station",
                "account": "Debit Card - Savings"
            },
            {
                "date": "2024-05-03",
                "merchant": "Hardware Store",
                "amount": 75.00,
                "category": "Groceries",
                "account": "Credit Card - American Express"
            },
            {
                "date": "2024-05-05",
                "merchant": "Clothing Boutique",
                "amount": 120.00,
                "category": "Clothing",
                "account": "Credit Card - Visa"
            },
            {
                "date": "2024-05-07",
                "merchant": "Utility Company",
                "amount": 150.00,
                "category": "Dining Out",
                "account": "Debit Card - Checking"
            },
            {
                "date": "2024-05-10",
                "merchant": "Coffee Shop",
                "amount": 10.25,
                "category": "Dining Out",
                "account": "Debit Card - Savings"
            },
            {
                "date": "2024-05-12",
                "merchant": "Online Retailer",
                "amount": 200.00,
                "category": "Clothing",
                "account": "Credit Card - Mastercard"
            },
            {
                "date": "2024-05-15",
                "merchant": "Fitness Center",
                "amount": 50.00,
                "category": "Gas Station",
                "account": "Debit Card - Checking"
            },
            {
                "date": "2024-05-17",
                "merchant": "Coffee Shop",
                "amount": 15.75,
                "category": "Dining Out",
                "account": "Debit Card - Savings"
            },
            {
                "date": "2024-05-20",
                "merchant": "Tech Store",
                "amount": 450.00,
                "category": "Gas Station",
                "account": "Credit Card - American Express"
            },
            {
                "date": "2024-05-25",
                "merchant": "Grocery Store",
                "amount": 85.00,
                "category": "Groceries",
                "account": "Credit Card - Visa"
            },
            {
                "date": "2024-05-27",
                "merchant": "Diner",
                "amount": 40.00,
                "category": "Dining Out",
                "account": "Credit Card - Mastercard"
            },
            {
                "date": "2024-05-30",
                "merchant": "Gas Station",
                "amount": 60.00,
                "category": "Gas Station",
                "account": "Debit Card - Checking"
            }
        ],
        "accounts": {

        },
        "budget": {
            "total": 800,
            "by_category": {
                "Gas Station": 250,
                "Dining Out": 250,
                "Groceries": 300
            }
        }
    }
}