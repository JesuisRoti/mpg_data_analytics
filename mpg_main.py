import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

from sqlalchemy import create_engine

from general_functions import (
    cleaning,
    top_pos,
    top_forward,
    top_backward,
    top_goal_keeper,
    top_midfielder,
)


def plot_players(
    colors: np.array,
    player_dataframe: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_step: float,
    y_step: float,
    x_leg: str,
    y_leg: str,
    title: str,
):
    fig, ax = plt.subplots()

    plt.yticks(
        np.arange(min(player_dataframe[y_col]), max(player_dataframe[y_col]), y_step)
    )
    plt.xticks(
        np.arange(min(player_dataframe[x_col]), max(player_dataframe[x_col]), x_step)
    )

    plt.grid(True)
    plt.title(title)
    ax.scatter(player_dataframe[x_col], player_dataframe[y_col], c=colors)

    legend_labels = []
    for j, name in enumerate(player_dataframe["playerFullName"]):
        legend_labels.append(ax.scatter([], [], c=colors[j], label=name))

    ax.legend(handles=legend_labels, bbox_to_anchor=(1, 1))

    ax.set_xlabel(x_leg)
    ax.set_ylabel(y_leg)

    fig.tight_layout()
    fig.show()


def add_extra_info(player_dataframe: pd.DataFrame):
    """
    This function will request mpg for more data about specific players, since it is one request per player this function
    should be used only for small dataframe.
    :param player_dataframe:
    :return: big json object containing all data for all the players in the dataframe
    """
    players_id = player_dataframe["pid"]
    url = "https://api.mpg.football/api/data/championship-player-stats/"
    players_full_stats_obj = {}

    for player in players_id.values:
        try:
            res = requests.get(f"{url}{player}/2023", timeout=300)
            data = res.json()
        except:
            print("Error during get request")
        else:
            players_full_stats_obj[player] = data
    return players_full_stats_obj


def clean_extra_data(fs_players: dict, original_dataframe: pd.DataFrame):
    """
    Function to clean and select valuables json attributes for players in the extra data received.
    :param fs_players: full stats players dictionary
    :param original_dataframe: dataframe containing basic information about top players
    :return: dataframe
    """
    df_fs_players = pd.DataFrame(fs_players).transpose()
    df_fs_players = df_fs_players["championships"]
    mercato_pick_rates = []
    for i in df_fs_players:
        # retrieve the main key
        key = list(i.keys())[0]
        main_stats = i[key]
        mercato_pick_rates.append(main_stats["mercatoPickRate"])

    original_dataframe["mercatoPR"] = mercato_pick_rates
    return original_dataframe


if __name__ == "__main__":
    res = requests.get(
        "https://api.mpg.football/api/data/championship-players-pool/2?season=2023",
        verify=False,
    )
    jdata = res.json()

    pd.set_option("float_format", "{:.2f}".format)

    df = pd.DataFrame(player for player in jdata["poolPlayers"])
    engine = create_engine("postgresql://postgres:root@localhost:5432/test_mpg")
    clean_df = cleaning(df)
    top_numb = 10
    top_pos = top_pos(clean_df, top_numb)
    best_forward = top_forward(top_pos)
    best_back = top_backward(top_pos)
    best_middle = top_midfielder(top_pos)
    best_goalk = top_goal_keeper(top_pos)

    extra_stats_bf = add_extra_info(best_forward)
    best_forward = clean_extra_data(extra_stats_bf, best_forward)

    colors_list = np.array(
        [
            "black",
            "red",
            "blue",
            "green",
            "skyblue",
            "lime",
            "pink",
            "orange",
            "maroon",
            "gray",
        ]
    )
    titles = ["Goal Keeper", "Mid Fielder", "Backward", "Forward"]
    granularity = [
        {
            "title": "Goal Keeper",
            "dataframe": best_goalk,
            "y_step": 0.1,
            "x_step": 2,
        },
        {
            "title": "Mid Fielder",
            "dataframe": best_middle,
            "y_step": 0.1,
            "x_step": 5,
        },
        {
            "title": "Backward",
            "dataframe": best_back,
            "y_step": 0.1,
            "x_step": 5,
        },
        {
            "title": "Forward",
            "dataframe": best_forward,
            "y_step": 0.1,
            "x_step": 5,
        },
    ]

    for i in granularity:
        plot_players(
            colors=colors_list,
            player_dataframe=i["dataframe"],
            x_col="quotation",
            y_col="averageRating",
            x_step=i["x_step"],
            y_step=i["y_step"],
            x_leg="Quotation",
            y_leg="Rating",
            title=i["title"],
        )


# df.to_sql('table_name', engine, if_exists='append')
