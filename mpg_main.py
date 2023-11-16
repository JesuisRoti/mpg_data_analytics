import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import requests

from sqlalchemy import create_engine
from adjustText import adjust_text


def cleaning(dirty_df: pd.DataFrame):
    df_stats = pd.DataFrame(stat for stat in dirty_df['stats'].values)

    # Get important columns from the original DF
    df_stats['playerFullName'] = dirty_df.agg(lambda x: f"{x['lastName']} {x['firstName'] or ''}", axis=1)
    df_stats['position'] = dirty_df['position'].replace({1: 'G', 2: 'D', 3: 'M', 4: 'A'})
    df_stats['pid'] = dirty_df['id']
    df_stats['participation'] = np.round(df_stats['totalPlayedMatches'] / df_stats['totalMatches'] * 100, 2)
    df_stats['quotation'] = dirty_df['quotation']

    # Drop useless ones and NA ratings
    df_stats = df_stats.drop(['nextMatch', 'quotationTrend', 'averagePointsTrend'], axis=1)
    df_stats = df_stats.dropna(subset=['averageRating', 'averagePoints'])
    df_stats = df_stats.astype({'averagePoints': 'int32', 'totalGoals': 'int32', 'totalStartedMatches': 'int32',
                                'totalPlayedMatches': 'int32'})

    return df_stats

def top_pos(dataf: pd.DataFrame, numb: int = 10):
    top_points_by_pos = dataf[dataf['participation'] > 75].groupby('position').apply(lambda group:
                                                                                              group.nlargest(numb,
                                                                                                     'averagePoints'))

    return top_points_by_pos

def top_forward(top_players: pd.DataFrame):
    return top_players[top_players['position'] == 'A']

def top_backward(top_players: pd.DataFrame):
    return top_players[top_players['position'] == 'D']

def top_middle(top_players: pd.DataFrame):
    return top_players[top_players['position'] == 'M']

def top_goalk(top_players: pd.DataFrame):
    return top_players[top_players['position'] == 'G']


def plot_players(colors: np.array, player_dataframe: pd.DataFrame, x_col: str, y_col: str, x_step: float,
                 y_step: float, x_leg: str, y_leg: str, title: str):
    fig, ax = plt.subplots()

    plt.yticks(np.arange(min(player_dataframe[y_col]), max(player_dataframe[y_col]), y_step))
    plt.xticks(np.arange(min(player_dataframe[x_col]), max(player_dataframe[x_col]), x_step))

    plt.grid(True)
    plt.title(title)
    ax.scatter(player_dataframe[x_col], player_dataframe[y_col], c=colors)

    legend_labels = []
    for j, name in enumerate(player_dataframe['playerFullName']):
        legend_labels.append(ax.scatter([], [], c=colors[j], label=name))

    ax.legend(handles=legend_labels, bbox_to_anchor=(1, 1))

    ax.set_xlabel(x_leg)
    ax.set_ylabel(y_leg)

    fig.tight_layout()
    fig.show()


if __name__ == '__main__':
    res = requests.get("https://api.mpg.football/api/data/championship-players-pool/2?season=2023", verify=False)
    jdata = res.json()

    pd.set_option('float_format', '{:.2f}'.format)

    df = pd.DataFrame(player for player in jdata['poolPlayers'])
    engine = create_engine('postgresql://postgres:root@localhost:5432/test_mpg')
    clean_df = cleaning(df)
    top_numb = 10
    top_pos = top_pos(clean_df, top_numb)
    best_forward = top_forward(top_pos)
    best_back = top_backward(top_pos)
    best_middle = top_middle(top_pos)
    best_goalk = top_goalk(top_pos)
    colors_list = np.array(['black', 'red', 'blue', 'green', 'skyblue', 'lime', 'pink', 'orange', 'maroon',
                            'gray'])
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
        }
    ]

    for i in range(len(granularity)):
        plot_players(colors=colors_list, player_dataframe=i['dataframe'], x_col='quotation', y_col='averageRating',
                 x_step=i['x_step'], y_step=i['y_step'], x_leg='Quotation', y_leg='Rating', title=i['title'])



# df.to_sql('table_name', engine, if_exists='append')


