import statsapi
import logging
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_sample_game_ids_for_year(year, sample_date_month=5, sample_date_day=15):
    """
    Tries to fetch a few game IDs for a sample date in a given year.
    """
    game_ids_found = []
    # statsapi.schedule expects MM/DD/YYYY
    date_str = f"{sample_date_month:02d}/{sample_date_day:02d}/{year}"
    logging.info(f"Attempting to fetch games for {date_str} (Year: {year})...")

    try:
        games = statsapi.schedule(date=date_str)
        if games:
            logging.info(f"Found {len(games)} games on {date_str}.")
            for game in games[:5]: # Get up to the first 5 games for the sample
                game_id = game.get('game_id')
                if game_id:
                    game_ids_found.append(str(game_id)) # Store as string for consistency
                else:
                    logging.warning(f"  Game found on {date_str} but is missing 'game_id'. Data: {game}")
        else:
            logging.info(f"No games found on {date_str}.")
    except Exception as e:
        logging.error(f"Error fetching games for {date_str}: {e}")
    
    return game_ids_found

if __name__ == "__main__":
    # Define years to sample.
    # Start with a very early year (high chance of no data from API)
    # Then some older years where API data might start appearing, and more recent ones.
    # Adjust these based on what you discover.
    current_year = datetime.now().year
    years_to_sample = [
        1876, # Start of National League (very unlikely to have API data)
        1903, # First modern World Series (unlikely)
        1920, # Older historical year
        1950, # Mid-century
        1970,
        1990,
        2000,
        2010,
        2020,
        current_year
    ]

    all_sampled_ids = {}

    for year in years_to_sample:
        ids = get_sample_game_ids_for_year(year)
        if ids:
            all_sampled_ids[year] = ids
        print("-" * 30)

    print("\n--- Summary of Sampled Game IDs ---")
    if all_sampled_ids:
        for year, ids in all_sampled_ids.items():
            print(f"Year {year}: Sample IDs = {', '.join(ids)}")
    else:
        print("No game IDs were successfully sampled from the API for the chosen years/dates.")

    print("\n--- Recommendations ---")
    print("1. Observe the format and magnitude of the sampled IDs from years where the API returns data.")
    print("2. For your backfilled historical data (e.g., 1871-19xx), it is STRONGLY recommended to use an ID system that is")
    print("   CLEARLY DISTINCT from the API's numeric IDs. Examples:")
    print("   - Use a prefix (e.g., 'HIST_1871_001')")
    print("   - Use negative integers if the API uses positive ones.")
    print("   - Use a completely separate numerical range (e.g., if API IDs are 6+ digits, use 1-5 digits for your own).")
    print("3. Relying on an ID being 'not currently used' by the API is risky for future compatibility.")