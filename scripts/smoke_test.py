\
import os
from luna.db import SupabaseDB

def main():
    url = os.getenv("SUPABASE_URL","")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY","") or os.getenv("SUPABASE_KEY","")
    if not url or not key:
        raise SystemExit("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    db = SupabaseDB(url, key)
    ok = db.ping()
    print("DB ping:", ok)

if __name__ == "__main__":
    main()
