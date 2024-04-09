import requests
from tabulate import tabulate


def get_fii_dii_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    url = 'https://www.nseindia.com/api/fiidiiTradeReact'
    with requests.session() as s:
        data = s.get(url, headers=headers)
        data = data.json()

        fii_data = {
            "name": data[1]['category'].replace('*', ''),
            "buy": data[1]['buyValue'],
            "sell": data[1]['sellValue'],
            "net": data[1]['netValue'],
            "date": data[1]['date']
        }

        dii_data = {
            "name": data[0]['category'].replace('*', ''),
            "buy": data[0]['buyValue'],
            "sell": data[0]['sellValue'],
            "net": data[0]['netValue'],
            "date": data[0]['date']
        }

        net_data = {
            "name": "Total",
            "buy": float(data[0]['buyValue']) + float(data[1]['buyValue']),
            "sell": float(data[0]['sellValue']) + float(data[1]['sellValue']),
            "net": float(data[0]['netValue']) + float(data[1]['netValue']),
            "date": ""
        }

        if net_data['net'] > 0:
            net_data.update({"color": 0x00FF00})
        else:
            net_data.update({"color": 0xFF0000})

        table = [
            ["FII", fii_data['date'], fii_data['buy'], fii_data['sell'],
                fii_data['net']],
            [dii_data['name'], dii_data['date'], dii_data['buy'], dii_data['sell'],
                dii_data['net']],
            [net_data['name'], net_data['date'], net_data['buy'], net_data['sell'],
                net_data['net']]
        ]
        return ["```\n" + tabulate(table, headers=(
            ["", "Date", "Buy", "Sell", "Net"]), tablefmt='simple_grid') + "\n```", net_data['color'],
            fii_data, dii_data, net_data
        ]


if __name__ == "__main__":
    fii_dii_data = get_fii_dii_data()
    print(fii_dii_data)
