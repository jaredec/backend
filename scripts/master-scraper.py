import statsapi
import pandas as pd
import time

def generate_golden_csv(start_year=1901, end_year=2025):
    print(f"🛰️ Starting Local Master Pull: {start_year} to {end_year}")
    master_batch = []
    
    # MASTER FILTERS VERIFIED BY AUDITS
    # F=Final, O=Game Over (Covers all shortened/tied variants)
    VALID_STATUS_PARENTS = ['F', 'O'] 
    # Regular + All Postseason + Tie-breakers
    VALID_GAME_TYPES = ['R', 'W', 'L', 'D', 'F', 'C', 'P']

    for year in range(start_year, end_year + 1):
        print(f"📅 Year {year}...", end="\r")
        try:
            # We pull WITHOUT hydration here for maximum stability
            # This ensures we hit the 2,430 ground truth for 2025
            data = statsapi.get('schedule', {
                'sportId': 1, 
                'startDate': f'01/01/{year}', 
                'endDate': f'12/31/{year}'
            })
            
            if not data.get('dates'): continue

            for date_obj in data['dates']:
                # FIX: Use the Official Standings Date from the date bucket
                official_date = date_obj['date']
                
                for g in date_obj['games']:
                    # 1. APPLY STATUS & TYPE FILTERS
                    if g.get('gameType') not in VALID_GAME_TYPES: continue
                    if g.get('status', {}).get('codedGameState') not in VALID_STATUS_PARENTS: continue

                    # 2. SCORE EXTRACTION
                    v_score = g.get('teams', {}).get('away', {}).get('score')
                    h_score = g.get('teams', {}).get('home', {}).get('score')

                    # 3. THE ERA-AWARE GHOST BUSTER (The '63' and '2430' Fix)
                    # Rule A: Discard if score is missing entirely
                    if v_score is None or h_score is None: continue
                    
                    # Rule B: Discard 0-0 if year > 1990 (Impossible modern ghost records)
                    if year > 1990 and v_score == 0 and h_score == 0: continue
                    
                    # Rule C: Exclude All-Star games mislabeled as 'R'
                    away_team = g.get('teams', {}).get('away', {}).get('team', {}).get('name', 'Unknown')
                    if "All-Star" in away_team: continue

                    master_batch.append({
                        "game_id": g['gamePk'],
                        "date": official_date,
                        "game_type": g['gameType'],
                        "league_id": g.get('league', {}).get('id', 0),
                        "status_code": g.get('status', {}).get('statusCode'),
                        "visitor_team": away_team,
                        "home_team": g.get('teams', {}).get('home', {}).get('team', {}).get('name', 'Unknown'),
                        "visitor_score": int(v_score),
                        "home_score": int(h_score),
                        "visitor_team_id": g.get('teams', {}).get('away', {}).get('team', {}).get('id'),
                        "home_team_id": g.get('teams', {}).get('home', {}).get('team', {}).get('id'),
                        "source": 'mlb_api'
                    })
            time.sleep(0.05) # Prevent rate limiting
        except Exception as e:
            print(f"\n❌ Error in {year}: {e}")

    if master_batch:
        df = pd.DataFrame(master_batch)
        # Deduplicate IDs: ensures the 'Final' version of a game wins over any placeholders
        df = df.sort_values('status_code').drop_duplicates(subset=['game_id'], keep='last')
        
        # Save to your laptop
        df.to_csv("golden_record_master.csv", index=False)
        print(f"\n\n🎉 SUCCESS! 'golden_record_master.csv' created with {len(df)} games.")
    else:
        print("❌ No data found.")

if __name__ == "__main__":
    generate_golden_csv()