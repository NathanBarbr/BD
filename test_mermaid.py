from app import _generate_mermaid

try:
    with open("CreateTables.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    print("--- SQL Content Read ---")
    
    mermaid = _generate_mermaid(sql_content)
    print("--- Mermaid Code Generated ---")
    print(mermaid[:500]) # Print first 500 chars
    print("...")
    print(mermaid[-100:]) # Print last 100 chars
except Exception as e:
    print(f"Error: {e}")
