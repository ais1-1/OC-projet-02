import requests
from bs4 import BeautifulSoup
import re
import csv

# function to create soup from a url
def creer_soup(url):
    reponse = requests.get(url)
    html_page = reponse.content

    # transforme en objet BeautifulSoup
    soup = BeautifulSoup(html_page, 'html.parser')
    return soup

## function to extract product details from a product page
def scrapper_un_page_produit(product_page_url):
    data = []
    data.append(product_page_url)
    #print("product page url is", product_page_url)

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
    #print("upc is ", upc)

    title = soup.find("h1").string
    data.append(title)
    #print("title is ", title)

    price_including_tax = second_column[3]
    data.append(price_including_tax)
    #print("price including tax is ", price_including_tax)

    price_excluding_tax = second_column[2]
    data.append(price_excluding_tax)
    #print("price excluding tax is ", price_excluding_tax)

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
    #print("number available is ", number_available)

    # get all meta tags
    all_metas = soup.find_all('meta')
    for meta in all_metas:
        if 'name' in meta.attrs and meta.attrs['name'] == 'description':
            #if the attribute 'name' is description assign the attribute 'content' to product description
            product_description = meta.attrs['content']
    data.append(product_description)
    #print("description is ", product_description)

    #get the ul part with class breadcrumb
    ul_elements = soup.find('ul', class_='breadcrumb')
    # get Category, which is the third li inside ul
    category = ul_elements.find_all('li')[2].text
    data.append(category)
    #print("category is ", category)

    #get the part with star rating
    star_ratings = soup.find('p', class_='star-rating')
    #get the second class name which indicates the number of stars
    review_rating = star_ratings['class'][1]
    data.append(review_rating)
    #print("review rating is", review_rating, "stars")

    #get the image tag
    image_tag = soup.find('img')
    #get the image url from the above result
    image_incomplete_url = image_tag['src']
    image_url = re.sub("\../..", product_page_url, image_incomplete_url)
    data.append(image_url)
    #print("image url is", image_url)

    return data

## function to add data to the created csv file
def append_row_fichier_csv(nom_de_fichier, data):
    # append data in csv file
    with open(nom_de_fichier, 'a+') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=',')
        writer.writerow(data)

## function to extract product links from a page
def get_product_links_from_page(soup_de_page):
    product_divs = soup_de_page.find_all('div', class_='image_container')
    product_links_from_a_page = []
    for item in product_divs:
        link = item.find('a')['href']
        full_link = re.sub("\A../../../", "http://books.toscrape.com/catalogue/", link)
        product_links_from_a_page.append(full_link)
    return product_links_from_a_page

## function to extract product links from a category page
def scrapper_page_category(category_page_url):
    # url d'une category à scrapper
    soup_category = creer_soup(category_page_url)
    #initialise product-links array
    product_links = []
    product_links = get_product_links_from_page(soup_category)

    # to get next pages in case of pagination
    next_page = soup_category.find('li', class_='next')

    if next_page:
        # to get total number of pages if there is a next page
        page_number_tag = soup_category.find('li', class_="current")
        page_number_text = page_number_tag.text
        # regex search for a list of all the digits present in the string and returns the 2nd in the list
        total_pages = int(re.findall(r'[0-9]+', page_number_text)[1])

        for i in range(total_pages-1):
            # get the next page url end
            next_page_url_end = next_page.find('a')['href']
            # remove the word index from the url and substitute next_page_url_end
            next_page_url = re.sub("index.html\Z", next_page_url_end, category_page_url)
            # create new soup for next page
            soup_category_next_page = creer_soup(next_page_url)

            product_links.extend(get_product_links_from_page(soup_category_next_page))
            # get next page
            next_page = soup_category_next_page.find('li', class_='next')
            print(i, total_pages, next_page_url)
    #print("product links of the category ", product_links)
    
    return product_links

def create_csv_for_a_category(name_of_the_file, link_to_the_category_page):
    # créer une liste des en-têtes
    en_tete = ["product_page_url", "universal_ product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]

    # créer fichier csv , write category name and write title row (en_tete) in it
    with open(name_of_the_file, 'w') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=',')
        writer.writerow(en_tete)

    # append data of each product in a category
    for link in scrapper_page_category(link_to_the_category_page):
        category_product_data = []
        category_product_data = scrapper_un_page_produit(link)
        append_row_fichier_csv(name_of_the_file, category_product_data)

def etl():
    # url de la page à scrapper
    #base_url = "http://books.toscrape.com"
    base_url = "http://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
    soup = creer_soup(base_url)
    create_csv_for_a_category("fiction.csv", base_url)
    
    
    ## create csv files for each category

## test
etl()
""" category_page_url = "http://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
#category_page_url = "http://books.toscrape.com/catalogue/category/books/classics_6/index.html"

data = scrapper_page_category(category_page_url)

   
creer_fichier_csv("test.csv", en_tete, data)
 """
""" link = '../../../bright-lines_11/index.html'
good_link = re.sub("\A../../../", "http://books.toscrape.com/catalogue/", link)
print(link, file=open("test.txt", "a"))
print(good_link, file=open("test.txt", "a") ) """