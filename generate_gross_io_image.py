import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import generate_oi_image
from datetime import datetime

isb_discord_link = "https://discord.gg/8MrqS6CASz"


def calculations(data):
    gross_oi = pd.DataFrame()
    gross_oi["index"] = data[0]["Client Type"]
    gross_oi["Long Futures"] = data[0]["Future Index Long"]
    gross_oi["Short Futures"] = data[0]["Future Index Short"]
    gross_oi["Net Futures"] = (
        data[0]["Future Index Long"] - data[0]["Future Index Short"]
    )
    gross_oi.drop(4, inplace=True)

    fut_change_oi = pd.DataFrame()
    fut_change_oi["Net Futures Change"] = (
        data[0]["Future Index Long"] - data[0]["Future Index Short"]
    ) - (data[1]["Future Index Long"] - data[1]["Future Index Short"])
    list_change_oi = fut_change_oi["Net Futures Change"].to_list()

    return gross_oi, list_change_oi


def generate_image(gross_oi, list_change_oi, date):
    # Melt the DataFrame to long format for Seaborn
    df_melted = pd.melt(
        gross_oi, id_vars="index", var_name="Category", value_name="Value"
    )

    # Rename the columns
    df_melted.columns = ["Participant", "Category", "Value"]

    # Filter out 'Net Futures' from the DataFrame
    df_melted_filtered = df_melted[df_melted["Category"] != "Net Futures"]

    # Map colors for each Category
    color_map = {"Long Futures": "#8fce00", "Short Futures": "#f44336"}

    # Custom X-axis labels
    custom_labels = gross_oi["Net Futures"].to_list()

    # Create the grouped bar graph using Seaborn
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(
        x="Participant",
        y="Value",
        hue="Category",
        data=df_melted_filtered,
        palette=color_map,
        dodge=True,
    )

    # Annotate the values on top of each bar
    for p in ax.patches:
        if p.get_height() > 0:  # Avoid annotating 0 values
            ax.annotate(
                f"{int(p.get_height()):,}",  # .0f}",
                (p.get_x() + p.get_width() / 2.0, p.get_height()),
                ha="center",
                va="center",
                xytext=(0, -10),
                textcoords="offset points",
            )

    # Annotate the values below the X-axis
    for label, x_position in zip(custom_labels, ax.get_xticks()):
        ax.annotate(
            f"{label:,}",
            (x_position, 0),
            ha="center",
            va="center",
            xytext=(0, -22),
            textcoords="offset points",
        )

    # Annotate the values below the X-axis
    for label, x_position in zip(list_change_oi, ax.get_xticks()):
        ax.annotate(
            f"({label:,})",
            (x_position, 0),
            ha="center",
            va="center",
            xytext=(0, -32),
            textcoords="offset points",
        )

    last_update = f"IndianStreetBets Discord: https://discord.gg/rp28AZA9Hb\nLast Update: {datetime.now().strftime('%d %b %Y %X')}"

    plt.xlabel("Participants")
    plt.ylabel("Open Interest")
    plt.yticks([])
    plt.suptitle(f"Gross OI Futures - {date}")
    # plt.suptitle(f"IndianStreetBets Discord: {isb_discord_link}", fontsize=10)
    plt.title(last_update, fontsize=8)
    plt.legend(loc="upper right")
    # plt.show()
    plt.savefig("Gross_OI.png", bbox_inches="tight")


if __name__ == "__main__":
    dates = generate_oi_image.get_dates()
    data_date = dates[2][0]
    data = generate_oi_image.get_oi_data(dates)
    oi, change_oi_list = calculations(data)
    generate_image(oi, change_oi_list, data_date)
