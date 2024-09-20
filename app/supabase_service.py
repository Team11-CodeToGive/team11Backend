from supabase import create_client, Client
from .config import Config

supabase: Client = None

def get_supabase_client():
    supabase_url = Config.SUPABASE_URL
    supabase_key = Config.SUPABASE_KEY
    global supabase
    supabase = create_client(supabase_url, supabase_key)
    return supabase