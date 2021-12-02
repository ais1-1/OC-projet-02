##
# SPDX-FileCopyrightText: 2021 Aiswarya Kaitheri Kandoth
#
#Authors :
# Aiswarya Kaitheri Kandoth
#
# SPDX-License-Identifier: GPL-3.0-or-later
##

import os
import requests
from bs4 import BeautifulSoup
import re
import csv
import shutil

## function to create soup from a url
def creer_soup(url):
    reponse = requests.get(url)
    html_page = reponse.content

    # transform to BeautifulSoup object
    soup = BeautifulSoup(html_page, 'html.parser')
    return soup

## function to extract product details from a product page
def scrapper_un_page_produit(product_page_url, base_url):
    data = []
    data.append(product_page_url)

    # create soup of the product page
    soup = creer_soup(product_page_url)

    # extract table rows
    table_rows = soup.find_all("table", class_="table")[0].find_all("tr")
    second_column = []
    # make an array with contents from 2nd column
    for row in table_rows:
        second_column.append(row.find_all('td')[0].text)
    # access the universal_product_code(upc)
    upc = second_column[0]
    data.append(upc)

    # access title
    title = soup.find("h1").string
    data.append(title)

    # access price including and excluding taxes
    price_including_tax = second_column[3]
    data.append(price_including_tax)

    price_excluding_tax = second_column[2]
    data.append(price_excluding_tax)

    ## function for geting integers from a sentence (replaced by regex re.search)
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

    # get all meta tags
    all_metas = soup.find_all('meta')
    for meta in all_metas:
        if 'name' in meta.attrs and meta.attrs['name'] == 'description':
            #if the attribute 'name' is description assign the attribute 'content' to product description
            product_description = meta.attrs['content']
    data.append(product_description)

    #get the ul part with class breadcrumb
    ul_elements = soup.find('ul', class_='breadcrumb')
    # get Category, which is the third li inside ul
    category = ul_elements.find_all('li')[2].text
    data.append(category)

    #get the part with star rating
    star_ratings = soup.find('p', class_='star-rating')
    #get the second class name which indicates the number of stars
    review_rating = star_ratings['class'][1]
    data.append(review_rating)

    #get the image tag
    image_tag = soup.find('img')
    #get the image url from the above result
    image_incomplete_url = image_tag['src']
    image_url = re.sub("\../..", base_url, image_incomplete_url)
    data.append(image_url)

    ## download images from each product urls visited

    # use os module to create folders to store image files if it does not exists
    # path to the main image folder
    path_to_image_folder = os.path.join("product_images")
    # path to category folder inside the image folder
    # replace white spaces with underscore for cleaner file names
    category_folder_name = re.sub(" ", "_", category)
    path_to_category_folder = os.path.join(path_to_image_folder, category_folder_name)

    if not os.path.exists(path_to_image_folder):
        os.mkdir(path_to_image_folder)

    # create folder for each category if it doesn't exist
    if not os.path.exists(path_to_category_folder):
        os.mkdir(path_to_category_folder)

    # get the file name with hash from image url which avoids same names of files
    image_file_name = re.split("\/", image_url)[-1]
    file_path = os.path.join(path_to_category_folder, image_file_name)

    # get streamed response; if stream is false content will be downloaded in the memory before returning
    image_reponse = requests.get(image_url, stream=True)

    # if requests is a success (200) do writing
    if image_reponse.status_code == 200:
        # open file in binary mode (b) for writing (w) the response
        with open(file_path, 'wb') as image_file:
            # decode the raw content
            image_reponse.raw.decode_content = True
            # save the image to the machine; shutil copy the content of the raw object to image_file object
            shutil.copyfileobj(image_reponse.raw, image_file)

    return data

## function to add data to the created csv file
def append_row_fichier_csv(csv_file_path, data):
    # append data in csv file
    with open(csv_file_path, 'a+') as fichier_csv:
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
    # create soup for a url of a category to extract
    soup_category = creer_soup(category_page_url)
    # initialise product-links array
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

    return product_links

def create_csv_for_a_category(name_of_the_file, link_to_the_category_page, base_url):
    # create a list of headers (en-têtes)
    en_tete = ["product_page_url", "universal_ product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]

    # replace white spaces with underscore
    name_of_the_file_without_space =re.sub(" ", "_", name_of_the_file)

    # create a folder to store csv files
    path_to_csv_folder = os.path.join("csv_files")
    if not os.path.exists(path_to_csv_folder):
        os.mkdir(path_to_csv_folder)

    # path to csv file
    csv_file_path = os.path.join(path_to_csv_folder, name_of_the_file_without_space)
    # if the csv file does not exist create one
    if not os.path.exists(csv_file_path):
        # create csv file , write category name and write headers (en_tete) in it
        with open(csv_file_path, 'w') as fichier_csv:
            writer = csv.writer(fichier_csv, delimiter=',')
            writer.writerow(en_tete)

    # append data of each product in a category
    for link in link_to_the_category_page:
        category_product_data = []
        category_product_data = scrapper_un_page_produit(link, base_url)
        append_row_fichier_csv(csv_file_path, category_product_data)

def etl():
    # url of the page to scrape
    base_url = "http://books.toscrape.com"
    soup = creer_soup(base_url)

    side_bar = soup.find('ul', class_='nav')
    list_of_category = side_bar.find_all('a')
    # get list of category names in a list
    category_name_list = []
    for item in list_of_category:
        text = item.text
        # strip the text and replace next line tag
        text = text.strip().replace('\n', '')
        category_name_list.append(text)
    # remove the title 'Books'
    category_name_list.pop(0)

    # create csv file names from category names
    csv_file_name_for_category = []
    for name in category_name_list:
        csv_file_name_for_category.append(name + '.csv')

    # get urls of every categories
    category_page_urls = []
    for link in list_of_category:
        category_url = link.get('href')
        # add base_url to get complete url to each category page
        category_complete_url = re.sub('catalogue', base_url + '/catalogue', category_url)
        category_page_urls.append(category_complete_url)
    category_page_urls.pop(0)

    # create a dictionary with csv_file_name_for_category as key and corresponding url as value
    dictionary_for_categories = dict(zip(csv_file_name_for_category, category_page_urls))

    # extract products data for each category in the website
    for item in dictionary_for_categories:
        links_from_categories = scrapper_page_category(dictionary_for_categories[item])
        create_csv_for_a_category(item, links_from_categories, base_url)

etl()