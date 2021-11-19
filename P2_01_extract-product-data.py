import requests
from bs4 import BeautifulSoup
import re
import csv

base_url = "http://books.toscrape.com"

# function to create soup from a url
def creer_soup(url):
    reponse = requests.get(url)
    html_page = reponse.content
    soup = BeautifulSoup(html_page, 'html.parser')
    return soup

# url de la category fiction à scrapper
category_page_url = "http://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
soup_category = creer_soup(category_page_url)

product_divs = soup_category.find_all('div', class_='image_container')
product_links = []
for item in product_divs:
    link = item.find('a')['href']
    product_links.append(link)
print(product_links)

next_page = soup_category.find('li', class_='next')
next_page_text = next_page.text
print("**********next page text is ", next_page_text)

if next_page_text == 'next':
    # get the next page url end
    next_page_url_end = next_page.find('a')['href']
    # remove the word index from the url and substitute next_page_url_end
    next_page_url = re.sub("index.html\Z", next_page_url_end, category_page_url)

##################################################$
# function to extract product details from a product page

# function to add data to the created csv file


#url de la produit 'the little prince' à scrapper
data = []
product_page_url = "http://books.toscrape.com/catalogue/the-little-prince_72/index.html"

data.append(product_page_url)
print("product page url is", product_page_url)

#parse le page HTML en objet Beautifulsoup
soup = creer_soup(product_page_url)

# extraire des ligne de la table
table_rows = soup.find_all("table", class_="table")[0].find_all("tr")
second_column = []
# faire un array avec les contenus de la deuxieme colonne
for row in table_rows:
    second_column.append(row.find_all('td')[0].text)
# acceder le universal_product_code(upc) 
upc = second_column[0]
data.append(upc)
print("upc is ", upc)

title = soup.find("h1").string
data.append(title)
print("title is ", title)

price_including_tax = second_column[3]
data.append(price_including_tax)
print("price including tax is ", price_including_tax)

price_excluding_tax = second_column[2]
data.append(price_excluding_tax)
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
data.append(number_available)
print("number available is ", number_available)

# get all meta tags
all_metas = soup.find_all('meta')
for meta in all_metas:
    if 'name' in meta.attrs and meta.attrs['name'] == 'description':
        #if the attribute 'name' is description assign the attribute 'content' to product description
        product_description = meta.attrs['content']
data.append(product_description)
print("description is ", product_description)

#get the ul part with class breadcrumb
ul_elements = soup.find('ul', class_='breadcrumb')
# get Category, which is the third li inside ul
category = ul_elements.find_all('li')[2].text
data.append(category)
print("category is ", category)

#get the part with star rating
star_ratings = soup.find('p', class_='star-rating')
#get the second class name which indicates the number of stars
review_rating = star_ratings['class'][1]
data.append(review_rating)
print("review rating is", review_rating, "stars")

#get the image tag
image_tag = soup.find('img')
#get the image url from the above result
image_incomplete_url = image_tag['src']
image_url = re.sub("\../..", base_url, image_incomplete_url)
data.append(image_url)
print("image url is", image_url)

# créer une liste des en-têtes
en_tete = ["product_page_url", "universal_ product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]

# créer fichier product_data.csv and write data in it
with open('product_data.csv', 'w') as fichier_csv:
    writer = csv.writer(fichier_csv, delimiter=',')
    writer.writerow(en_tete)
    writer.writerow(data)
