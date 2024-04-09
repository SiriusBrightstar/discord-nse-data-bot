import json
import requests
import traceback
from pandas import DataFrame
from datetime import datetime
from datetime import timedelta

niftyindices_headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://niftyindices.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://niftyindices.com/reports/historical-data',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
}

date_url = 'https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString'


def index_history(symbol, start_date, end_date):
    try:
        data = {"name": symbol,
                "startDate": start_date,
                "endDate": end_date,
                }
        data = {"cinfo": json.dumps(data)}
        payload = requests.post(url=date_url,
                                timeout=300, headers=niftyindices_headers, json=data,).json()
        payload = json.loads(payload["d"])
        payload = DataFrame.from_records(payload)
        return payload
    except Exception as e:
        print(traceback.format_exc())
        raise Exception(e)


if __name__ == "__main__":
    today = datetime.now()
    previous_date_5 = today - timedelta(5)
    historical_data = index_history(
        "NIFTY 50",
        f"{previous_date_5.strftime('%d-%b-%Y')}",
        f"{today.strftime('%d-%b-%Y')}",
    )

    list_of_past_dates = list(historical_data["HistoricalDate"])
    print(list_of_past_dates)
