# Extracting data from "Books to Scrape"

This is a project done as part of my degree program at Openclassrooms.

It involves extracting data from the "[Books to Scrape](http://books.toscrape.com/)" website and storing them in a csv file. The script will create a directory named *csv_files* and csv files will be stored inside with corresponding category names. Also download and save the image file for each product page inside directories with corresponding category names, which is in a directory called *product_images*.

Directory structure will look like this :

```
projectName
|   .gitignore
|   LICENSE
|   P2_01_extract-product-data.py
│   README.md
│   requirements.txt    
│
└───csv_files
│   │   <Category_name>.csv
│   │   ...
│   
└───product_images
    │
    └───<Category_name>
        │   <image>.jpg
        |   ...

```

## Create a virtual environment

Requirement : Python3.3 or later

Open terminal at the root of the project directory, and enter the following command:

    python -m venv <name of the virtual environment>

For example:

    python -m venv env

This will create a directory named *env* inside your project directory.

## Activate the virtual environment

In the project directory, open a terminal and enter the following command:

    source <name of the virtual environment>/bin/activate

## Install dependencies

Again, inside the project directory, in your terminal, enter the following command:

    pip install -r requirements.txt

This will install all the required modules to run the python script.

## Execute the python script

In your terminal inside the project directory:

    python P2_01_extract-product-data.py

