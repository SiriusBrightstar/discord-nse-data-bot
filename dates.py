import pytz
import traceback
import yfinance as yf


def index_history():
    try:
        nsei = yf.Ticker("^NSEI")
        df = nsei.history(period="5d")

        # Get the last two dates from the index
        last_two_dates = df.index[-2:]

        # Convert numpy datetime64 objects to datetime objects in IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        last_two_dates_ist = [date.tz_localize(
            None).tz_localize(ist) for date in last_two_dates]

        # Convert to strings in the format '%d-%b-%Y'
        last_two_dates_str = [date.strftime('%d %b %Y')
                              for date in last_two_dates_ist]

        return last_two_dates_str
    except Exception as e:
        print(traceback.format_exc())
        raise Exception(e)


if __name__ == "__main__":
    list_of_past_dates = index_history()
    print(list_of_past_dates)
