try:
    from psycopg2.rows import dict_row
    print('SUCCESS: psycopg2.rows.dict_row is available')
except Exception as e:
    print(f'FAIL: {e}') 