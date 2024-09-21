from supabase import create_client, Client
from .config import Config

supabase: Client = None

def get_supabase_client():
    supabase_url = 'https://lxnzcyuzjvmdlgizhwwq.supabase.co'
    supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4bnpjeXV6anZtZGxnaXpod3dxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNjg2ODY1NSwiZXhwIjoyMDQyNDQ0NjU1fQ.lYoqL8TJWQkbWutzn5ZaYKjS1BtQTgpw_E09LUxAkCY'
    global supabase
    supabase = create_client(supabase_url, supabase_key)
    return supabase