import requests
from bs4 import BeautifulSoup
import re

#url de la produit 'the little prince' à scrapper
product_page_url = "http://books.toscrape.com/catalogue/the-little-prince_72/index.html"
reponse = requests.get(product_page_url)
html_page = reponse.content
#print(html_page)

#parse le page HTML en objet Beautifulsoup
soup = BeautifulSoup(html_page, 'html.parser')

# extraire des ligne de la table
table_rows = soup.find_all("table", class_="table")[0].find_all("tr")
second_column = []
# faire un array avec les contenus de la deuxieme colonne
for row in table_rows:
    second_column.append(row.find_all('td')[0].text)
print(second_column)
# acceder le universal_product_code(upc) 
upc = second_column[0]
print("upc***", upc)

title = soup.find("h1")
print(title.string)

price_including_tax = second_column[3]
print(price_including_tax)

price_excluding_tax = second_column[2]
print(price_excluding_tax)

# function pour recuperer l'entier depuis une phrase (remplacé par regex re.search)
'''def get_int_from_string(availability):
    list_of_words = availability.split("(")[1].split()
    for i in list_of_words:
        if i.isdigit():
            number_available = i
    return number_available
'''

availability_detail = second_column[5]
number_available = int(re.search(r'\d+', availability_detail).group())
print(number_available)

product_description = soup.find(attrs={"name":"description"})
print("descriptions****", product_description)

#category, 3rd element in breadcrumbs
#review_rating, probably with css selector
#image_url, dans tag img src

# use css selector for example, in inspect element, right click description => .product_page > p:nth-child(3)
#print("attr---", soup.table.attrs) to find attribute of an element
#print(soup.select_one(".product_page > p:nth-child(3)"))
#print(soup.get_text())