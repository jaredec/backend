import statsapi

def check_api_lineage(team_id):
    print(f"🕵️ Fetching official MLB history for Team ID: {team_id}...")
    
    # We use the team endpoint with 'pastNames' hydration
    try:
        # Note: we use the raw get to access the hydrated fields
        data = statsapi.get('team', {'teamId': team_id, 'hydrate': 'pastNames'})
        
        team_data = data['teams'][0]
        print(f"\nFranchise: {team_data['name']} ({team_data['abbreviation']})")
        print("-" * 50)
        
        # Check for the pastNames array
        past_names = team_data.get('pastNames', [])
        
        if not past_names:
            print("No past names found in API for this ID.")
            return

        print(f"{'Team Name':<30} | {'Season Range'}")
        print("-" * 50)
        for p in past_names:
            # The API provides the first and last year for each identity
            print(f"{p['teamName']:<30} | {p['seasonStartYear']} - {p['seasonEndYear']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api_lineage(119)