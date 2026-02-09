import psycopg2

# --- CONNECTION ---
DATABASE_URL = process.env.DATABASE_URL #adjust this as needed

def bulk_upload_to_supabase():
    print("🚀 Streaming master CSV to Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    with open('golden_record_master.csv', 'r') as f:
        next(f) # Skip the header row
        try:
            cur.copy_from(f, 'public.gamelogs', sep=',', columns=(
                'game_id', 'date', 'game_type', 'league_id', 'status_code', 
                'visitor_team', 'home_team', 'visitor_score', 'home_score', 
                'visitor_team_id', 'home_team_id', 'source'
            ))
            conn.commit()
            print("✅ Bulk upload complete!")
        except Exception as e:
            print(f"❌ Error during bulk upload: {e}")
            conn.rollback()
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    bulk_upload_to_supabase()