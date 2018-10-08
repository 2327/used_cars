from .dbtools import Base_Updater, Data_Getter


item1 = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '150000', 'price': '560000'}
item11 = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '135480', 'price': '600000'}
item12 = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '135480', 'price': '610000'}
item13 = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '135480', 'price': '560000'}
item2 = {'brand': 'Volvo', 'model': 'S60', 'year': '2011', 'kmage': '145480', 'price': '560000'}
item = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '135000'}

items = [item1, item2, item11, item12, item13]

updater = Base_Updater()
updater.start_updating()
for i in items:
    updater.update(i)
updater.end_updating()

getter = Data_Getter()
for brand in getter.get_brands():
    print(brand)

for model in getter.get_models('Volvo'):
    print(model)

getter._round5_mileage({'hello': 'hello'})

print(getter.get_avg_price(item))
print(getter.get_prices(item))
