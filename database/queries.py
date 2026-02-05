# database/queries.py
"""
کوئری‌های SQL آماده برای استفاده در برنامه
"""

# ==================== کوئری‌های ورودی پوشاک ====================
QUERY_INSERT_GARMENT_ENTRY = '''
    INSERT INTO garment_entries 
    (product_name, product_code, size, color, custom_color, fabric_type, 
     entry_date, tailor_name, quantity, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

QUERY_SELECT_ALL_ENTRIES = '''
    SELECT id, product_code, product_name, color, size, fabric_type, 
           entry_date, tailor_name, quantity, notes, created_at
    FROM garment_entries 
    ORDER BY entry_date DESC, created_at DESC 
    LIMIT ?
'''

QUERY_SELECT_ENTRY_BY_CODE = '''
    SELECT * FROM garment_entries WHERE product_code = ?
'''

QUERY_DELETE_ENTRY = '''
    DELETE FROM garment_entries WHERE product_code = ?
'''

QUERY_UPDATE_ENTRY_QUANTITY = '''
    UPDATE garment_entries SET quantity = ? WHERE product_code = ?
'''

QUERY_SEARCH_ENTRIES = '''
    SELECT * FROM garment_entries 
    WHERE product_code LIKE ? OR product_name LIKE ? OR color LIKE ? 
    OR tailor_name LIKE ? OR fabric_type LIKE ?
    ORDER BY entry_date DESC 
    LIMIT ?
'''

QUERY_GET_INVENTORY = '''
    SELECT color, size, SUM(quantity) as total
    FROM garment_entries
    GROUP BY color, size
    ORDER BY color, size
'''

# ==================== کوئری‌های خروجی پوشاک ====================
QUERY_INSERT_GARMENT_OUTPUT = '''
    INSERT INTO garment_outputs 
    (product_code, output_date, quality, destination, quantity, package_code, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
'''

QUERY_SELECT_ALL_OUTPUTS = '''
    SELECT id, product_code, output_date, quality, destination, 
           quantity, package_code, notes, created_at
    FROM garment_outputs 
    ORDER BY output_date DESC, created_at DESC 
    LIMIT ?
'''

QUERY_DELETE_OUTPUT = '''
    DELETE FROM garment_outputs WHERE id = ?
'''

QUERY_GET_TODAY_OUTPUTS = '''
    SELECT COUNT(*), SUM(quantity) 
    FROM garment_outputs 
    WHERE output_date = ?
'''

# ==================== کوئری‌های کارمندان ====================
QUERY_INSERT_EMPLOYEE = '''
    INSERT INTO employees 
    (first_name, last_name, national_id, birth_date, address, phone,
     position, hire_date, salary, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

QUERY_SELECT_ALL_EMPLOYEES = '''
    SELECT id, first_name, last_name, national_id, position, 
           phone, hire_date, status, salary
    FROM employees 
    ORDER BY last_name, first_name
'''

QUERY_DELETE_EMPLOYEE = '''
    DELETE FROM employees WHERE national_id = ?
'''

QUERY_COUNT_ACTIVE_EMPLOYEES = '''
    SELECT COUNT(*) FROM employees WHERE status = 'فعال'
'''

# ==================== کوئری‌های گزارشات ====================
QUERY_DAILY_REPORT = '''
    SELECT 
        (SELECT COUNT(*) FROM garment_entries WHERE entry_date = ?) as entry_count,
        (SELECT SUM(quantity) FROM garment_entries WHERE entry_date = ?) as entry_quantity,
        (SELECT COUNT(*) FROM garment_outputs WHERE output_date = ?) as output_count,
        (SELECT SUM(quantity) FROM garment_outputs WHERE output_date = ?) as output_quantity
'''

QUERY_MONTHLY_REPORT = '''
    SELECT 
        (SELECT COUNT(*) FROM garment_entries WHERE strftime('%Y-%m', entry_date) = ?) as entry_count,
        (SELECT SUM(quantity) FROM garment_entries WHERE strftime('%Y-%m', entry_date) = ?) as entry_quantity,
        (SELECT COUNT(*) FROM garment_outputs WHERE strftime('%Y-%m', output_date) = ?) as output_count,
        (SELECT SUM(quantity) FROM garment_outputs WHERE strftime('%Y-%m', output_date) = ?) as output_quantity
'''

QUERY_TOTAL_STATS = '''
    SELECT 
        (SELECT COUNT(*) FROM garment_entries) as total_entries,
        (SELECT SUM(quantity) FROM garment_entries) as total_inventory,
        (SELECT COUNT(*) FROM garment_outputs) as total_outputs,
        (SELECT COUNT(*) FROM employees WHERE status = 'فعال') as active_employees
'''