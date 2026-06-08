import traceback
import pytz
from datetime import datetime, timedelta
import pandas_market_calendars as mcal


def index_history():
    try:
        # Define IST timezone
        ist = pytz.timezone('Asia/Kolkata')

        # Use NSE trading calendar
        nse = mcal.get_calendar('NSE')

        # Get trading schedule for the past 10 days
        today = datetime.now().date()
        start_date = today - timedelta(days=10)
        schedule = nse.schedule(start_date=start_date.strftime('%Y-%m-%d'),
                                end_date=today.strftime('%Y-%m-%d'))

        # Extract the last two trading dates
        last_two_dates = schedule.index[-2:]

        # Convert to market close time in IST
        last_two_dates_ist = [
            schedule.loc[date]['market_close'].tz_convert(ist)
            for date in last_two_dates
        ]

        # Format as strings
        last_two_dates_str = [
            date.strftime('%d %b %Y') for date in last_two_dates_ist
        ]
        last_two_dates_str.reverse()  # Latest date first

        return last_two_dates_str

    except Exception as e:
        print(traceback.format_exc())
        raise Exception(e)


if __name__ == "__main__":
    list_of_past_dates = index_history()
    print(list_of_past_dates)
