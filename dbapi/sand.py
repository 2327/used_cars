from dbtools import Base_Updater, Data_Getter


item1 = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '135480', 'price': '560000'}
item2 = {'brand': 'Volvo', 'model': 'S60', 'year': '2011', 'kmage': '145480', 'price': '560000'}
item = {'brand': 'VW', 'model': 'Golf', 'year': '2010', 'kmage': '135000'}

updater = Base_Updater()
updater.start_updating()
for i in range(5):
    updater.update(item1)
for i in range(5):
    updater.update(item2)
updater.end_updating()

getter = Data_Getter()
for brand in getter.get_brands():
    print(brand)

print(getter.get_price(item))
