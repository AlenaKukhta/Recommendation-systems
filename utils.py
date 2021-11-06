import pandas as pd
import numpy as np


def prefilter_items(data, take_n_popular=5000, item_features=None):
    # Уберем не интересные для рекомендаций категории (department)
    if item_features is not None:
        department_size = pd.DataFrame(item_features. \
                                       groupby('department')['item_id'].nunique(). \
                                       sort_values(ascending=False)).reset_index()

        department_size.columns = ['department', 'n_items']
        rare_departments = department_size[department_size['n_items'] < 150].department.tolist()
        items_in_rare_departments = item_features[
            item_features['department'].isin(rare_departments)].item_id.unique().tolist()

        data = data[~data['item_id'].isin(items_in_rare_departments)]

    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    data['price'] = data['sales_value'] / (np.maximum(data['quantity'], 1))
    data = data[data['price'] > 2]

    # Уберем слишком дорогие товары
    data = data[data['price'] < 50]

    # Возьмем топ по популярности
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)

    top = popularity.sort_values('n_sold', ascending=False).head(take_n_popular).item_id.tolist()

    # Заведем фиктивный item_id (если юзер покупал товары из топ-5000, то он "купил" такой товар)
    data.loc[~data['item_id'].isin(top), 'item_id'] = 999999


    return data

def postfilter_items(user_id, recommednations):
    pass



# def prefilter_items(data, item_features):
#     # Оставим только 5000 самых популярных товаров
#     popularity = data.groupby('item_id')['quantity'].sum().reset_index()
#     popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
#     top_5000 = popularity.sort_values('n_sold', ascending=False).head(5000).item_id.tolist()
#
#     # добавим, чтобы не потерять юзеров
#     data.loc[~data['item_id'].isin(top_5000), 'item_id'] = 999999
#
#     # Уберем самые популярные
#     popularity_2 = data.groupby('item_id')['quantity'].count().reset_index()
#
#     max_popular_items = popularity_2[popularity_2['quantity'] > 5000]['item_id'].tolist()
#     data = data[~data['item_id'].isin(max_popular_items)]
#
#     # Уберем самые непопулряные
#     min_popular_items = popularity_2[popularity_2['quantity'] == 1]['item_id'].tolist()
#     data = data[~data['item_id'].isin(min_popular_items)]
#
#     # # Уберем товары, которые не продавались за последние 12 месяцев
#     last_12_months = data.loc[data['week_no'] > 52].item_id.tolist()
#     data.loc[~data['item_id'].isin(last_12_months), 'item_id'] = 999999
#
#     # Уберем не интересные для рекомендаций категории (department)
#     data = data.loc[~data['item_id'].isin(item_features.loc[item_features.department == 'RX', :].item_id.unique()), :]
#
#     # # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
#     data['price'] = data['sales_value'] / data['quantity']
#     data = data.loc[data['price'] > 0.5, :]
#
#     # Уберем слишком дорогие товары
#     data = data.loc[data['price'] < 200, :]
#     data = data.drop(['price'], axis=1)
#
#     return data