import requests
from bs4 import BeautifulSoup
import re

#url de la produit 'the little prince' à scrapper
product_page_url = "http://books.toscrape.com/catalogue/the-little-prince_72/index.html"
reponse = requests.get(product_page_url)
html_page = reponse.content
print("product page url is", product_page_url)

#parse le page HTML en objet Beautifulsoup
soup = BeautifulSoup(html_page, 'html.parser')

# extraire des ligne de la table
table_rows = soup.find_all("table", class_="table")[0].find_all("tr")
second_column = []
# faire un array avec les contenus de la deuxieme colonne
for row in table_rows:
    second_column.append(row.find_all('td')[0].text)
# acceder le universal_product_code(upc) 
upc = second_column[0]
print("upc is ", upc)

title = soup.find("h1")
print("title is ", title.string)

price_including_tax = second_column[3]
print("price including tax is ", price_including_tax)

price_excluding_tax = second_column[2]
print("price excluding tax is ", price_excluding_tax)

# function pour recuperer l'entier depuis une phrase (remplacé par regex re.search)
'''def get_int_from_string(availability):
    list_of_words = availability.split("(")[1].split()
    for i in list_of_words:
        if i.isdigit():
            number_available = i
    return number_available
'''

availability_detail = second_column[5]
''' Utilisation de regex pour séparer le numéro de la chaîne de caractères,
le "r" au début permet de s'assurer que la chaîne est traitée comme une "chaîne brute",
\d renvoie une correspondance lorsque la chaîne contient des chiffres (de 0 à 9),'+' pour une ou plusieurs occurrences,
group() renvoie la partie de la chaîne de caractères pour laquelle il y a une correspondance,
et int() transforment le résultat entier en nombre entier.'''
number_available = int(re.search(r'\d+', availability_detail).group())
print("number available is ", number_available)

# get all meta tags
all_metas = soup.find_all('meta')
for meta in all_metas:
    if 'name' in meta.attrs and meta.attrs['name'] == 'description':
        #if the attribute 'name' is description assign the attribute 'content' to product description
        product_description = meta.attrs['content']
print("description is ", product_description)

#get the ul part with class breadcrumb
ul_elements = soup.find('ul', class_='breadcrumb')
# get Category, which is the third li inside ul
category = ul_elements.find_all('li')[2].text
print("category is ", category)

#get the part with star rating
star_ratings = soup.find('p', class_='star-rating')
#get the second class name which indicates the number of stars
review_rating = star_ratings['class'][1]
print("review rating is", review_rating, "stars")

#get the image tag
image_tag = soup.find('img')
#get the image url from the above result
image_url = image_tag['src']
print("image url is", image_url)
#image_url, dans tag img src