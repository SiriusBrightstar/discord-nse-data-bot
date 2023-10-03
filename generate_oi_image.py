import df2img
from nsepython import *
from io import StringIO
from requests import get
from datetime import datetime
from datetime import timedelta
from pandas import read_csv

url = "https://archives.nseindia.com/content/nsccl/fao_participant_oi_"


def get_dates() -> list:
    try:
        # Get Previous Market Open Dates
        today = datetime.now()
        previous_date_5 = today - timedelta(5)

        historical_data = index_history(
            "NIFTY 50",
            f"{previous_date_5.strftime('%d-%b-%Y')}",
            f"{today.strftime('%d-%b-%Y')}",
        )

        list_of_past_dates = list(historical_data["HistoricalDate"])
        # print(list_of_past_dates)

        # Convert Dates to get Participant wise OI Data
        previous_date_1 = datetime.strptime(list_of_past_dates[1], "%d %b %Y").strftime(
            "%d%m%Y"
        )
        url_1 = url + str(previous_date_1) + ".csv"

        previous_date_0 = datetime.strptime(list_of_past_dates[0], "%d %b %Y").strftime(
            "%d%m%Y"
        )
        url_0 = url + str(previous_date_0) + ".csv"

        return [url_0, url_1, [list_of_past_dates[0], list_of_past_dates[1]]]
    except Exception as e:
        print(f"Error getting dates: {e}")
        return None


def get_oi_data(url_w_dates) -> list:
    try:
        # Request Participant wise OI Data
        csv_0 = get(url=url_w_dates[0])
        csv_1 = get(url=url_w_dates[1])

        if (csv_0.status_code == 200) and (csv_1.status_code == 200):
            data_0 = StringIO(csv_0.content.decode("utf-8"))
            df_0 = read_csv(data_0, skiprows=1)
            # print(df_0.T)

            print("Successfully received data from NSE")
            data_1 = StringIO(csv_1.content.decode("utf-8"))
            df_1 = read_csv(data_1, skiprows=1)
            # print(df_1)
            return [df_0, df_1, url_w_dates[2]]
        else:
            print(
                f"Failed to get response. Status Code: {csv_0.status_code} & {csv_1.status_code}"
            )

    except Exception as e:
        print(f"Error getting data: {e}")


def calculate_oi_change(data):
    # Calculate Change in IO

    data[1]["Index FUT"] = data[1]["Future Index Long"] - data[1]["Future Index Short"]
    data[1]["Stock FUT"] = (
        data[1]["Future Stock Long"] - data[1]["Future Stock Short\t"]
    )
    data[1]["Total CALL"] = (
        data[1]["Option Index Call Long"] - data[1]["Option Index Call Short"]
    )

    data[1]["Total PUT"] = (
        data[1]["Option Index Put Long"] - data[1]["Option Index Put Short"]
    )
    data[1]["Net Index Option"] = data[1]["Total CALL"] - data[1]["Total PUT"]

    # print(f"OI Data for {data[2][1]}")
    # print(data[1][["Client Type", "Total Long Contracts\t", "Total Short Contracts"]])

    data[0]["Index FUT"] = data[0]["Future Index Long"] - data[0]["Future Index Short"]
    data[0]["Stock FUT"] = (
        data[0]["Future Stock Long"] - data[0]["Future Stock Short\t"]
    )
    data[0]["Total CALL"] = (
        data[0]["Option Index Call Long"] - data[0]["Option Index Call Short"]
    )
    data[0]["Total PUT"] = (
        data[0]["Option Index Put Long"] - data[0]["Option Index Put Short"]
    )
    data[0]["Net Index Option"] = data[0]["Total CALL"] - data[0]["Total PUT"]

    # print(f"OI Data for {data[2][0]}")
    # print(data[0][["Client Type", "Total Long Contracts\t", "Total Short Contracts"]])

    net_df = pd.DataFrame()
    net_df["Participant"] = data[0]["Client Type"]
    net_df["Index FUT"] = data[0]["Index FUT"] - data[1]["Index FUT"]
    net_df["Stock FUT"] = data[0]["Stock FUT"] - data[1]["Stock FUT"]
    net_df["Total CALL"] = data[0]["Total CALL"] - data[1]["Total CALL"]
    net_df["Total PUT"] = data[0]["Total PUT"] - data[1]["Total PUT"]
    net_df["Net Index Option"] = (
        data[0]["Net Index Option"] - data[1]["Net Index Option"]
    )
    net_df["Net View (FUT+OPT) OI"] = net_df["Index FUT"] + net_df["Net Index Option"]
    net_df["View"] = [
        "Bullish" if x >= 0 else "Bearish" for x in net_df["Net Index Option"]
    ]
    heading = f"Net OI Change between {data[2][1]} & {data[2][0]}"
    net_df.drop(4, inplace=True)
    net_df.set_index("Participant", drop=True, inplace=True)
    return [net_df, heading]


def save_img(data):
    try:
        fig = df2img.plot_dataframe(
            data[0],
            title=dict(
                font_color="black",
                font_size=18,
                text=data[1],
                xanchor="auto",
            ),
            row_fill_color=("#ffffff", "#d7d8d6"),
            fig_size=(700, 200),
            show_fig=False,
        )
        df2img.save_dataframe(fig=fig, filename="plot1.png")
    except Exception as e:
        print(f"Error generating image: {e}")


if __name__ == "__main__":
    dates = get_dates()
    data = get_oi_data(dates)
    oi_data = calculate_oi_change(data)
    save_img(oi_data)
