# Data manipulation
import pandas as pd 
from statistics import mode

# Geocode finder
import pgeocode
import geopy.distance

# Web scraper
import requests
from bs4 import BeautifulSoup
import re

#%%
df_lfl = pd.read_csv(r'/Users/firatsoydinc/Desktop/Coding/Recommendation System /Book_csv/csv_files/cleaned_lfl_geocodes.csv')
df_lfl = df_lfl.rename(columns={'longitude' : 'latitude','latitude':'longitude'})



#%%

def geocode_finder ():
    nomi = pgeocode.Nominatim('nl')
    postal_code = input('Please enter your postal code')
    postal_code= str(postal_code)
    a = nomi.query_postal_code(postal_code)
    a = a.to_frame().reset_index()
    geo_codes = a[(a['index'] == 'latitude') | (a['index'] == 'longitude')]
    geo_codes.reset_index(drop= True, inplace=True)
    geo_codes=geo_codes.rename(columns={'index':'geotype',0:'geo_number'})
    geo_codes["geo_number"] = pd.to_numeric(geo_codes["geo_number"], downcast="float")
    global latitude
    global longitude
    latitude = geo_codes[0:1]
    longitude= geo_codes[1:2]

    return latitude,longitude

#%%
def closest_pop_up_libraries():
    nomi = pgeocode.Nominatim('nl')
    postal_code = input('Please enter your postal code')
    postal_code= str(postal_code)
    a = nomi.query_postal_code(postal_code)
    a = a.to_frame().reset_index()
    geo_codes = a[(a['index'] == 'latitude') | (a['index'] == 'longitude')]
    geo_codes.reset_index(drop= True, inplace=True)
    geo_codes=geo_codes.rename(columns={'index':'geotype',0:'geo_number'})
    geo_codes["geo_number"] = pd.to_numeric(geo_codes["geo_number"], downcast="float")
    global latitude
    global longitude
    latitude = geo_codes[0:1]
    longitude= geo_codes[1:2]
    
    coords_user = (latitude.geo_number[0],longitude.geo_number[1])
    global liste
    liste = []
    df_lfl['distance'] = 0.00000
    for index,i in enumerate(range(len(df_lfl)-1)):
        coords_lfl = (df_lfl['latitude'][i],df_lfl['longitude'][i])
        a = geopy.distance.geodesic(coords_user, coords_lfl).km
        a = round(a,5)
        df_lfl['distance'][index] = a
    loc = df_lfl.sort_values(by = 'distance')
    for index_1,each in enumerate(loc.distance[0:3]):
        close_url= df_lfl.links[index_1]
        page = requests.get(close_url)
        html = BeautifulSoup(page.content, "html.parser") 
        # functional name
        info_adress = html.find_all(class_ = "item-info")
        info_adress = str(info_adress)
        
        regex_adress = (r"<dd class=\"data\">[a-zA-Z]*\s[a-zA-Z0-9\s]*")
        matches_adress = re.finditer(regex_adress, info_adress, re.MULTILINE)
        adress = ''
        for matchNum, match in enumerate(matches_adress, start=1):
            adress =  ("{match}".format(match = match.group()))      
            adress = adress.replace('<dd class="data">', '')
            
        print('The closest library is in',adress,round(each,5),'km away')
    
    #%%
def isbn_adder():
    global isbn_list
    isbn_list = [] 
    q = input  ("do you want to write another isbn number? yes/no")
    q=q.lower()
    while q == 'yes':
        if (q.lower() =='y') | (q.lower()== 'yes'):
            isbn = input ("please enter isbn number of the book")
            isbn_list.append(isbn)
            q = input  ("do you want to write another isbn number? ")

        else:
            return isbn_list
        
        #%%
global user_df
user_df = pd.DataFrame()
def book_adder () :
    isbn_adder()
    global new_user_df
    new_user_df = pd.DataFrame()
    for each in isbn_list:

        base_url = 'https://www.bookfinder.com/search/?isbn='+each+'&mode=isbn&st=sr&ac=qr'
        page = requests.get(base_url)
        html = BeautifulSoup(page.content, "html.parser")
        info_isbn_check = html.find_all(align = 'center')
        text_isbn_check = (str(info_isbn_check))
        regex_isbn_check = r"Sorry, we found no matching results at this time"

        matches_isbn_check = re.finditer(regex_isbn_check, text_isbn_check, re.MULTILINE)

        isbn_check = ''
        for matchNum, match in enumerate(matches_isbn_check, start=1):

            isbn_check= ("{match}".format(match = match.group()))
            print(isbn_check)

        if isbn_check == '':
            print('Processing')
            info = html.find_all(class_ = "attributes")
            text = (str(info))

            regex_name = r"\"name\">[a-zA-z\s\W]*[a-zA-z\s0-9()]*</span>"
            matches_name = re.finditer(regex_name, text, re.MULTILINE)

            for matchNum, match in enumerate(matches_name, start=1):

                name_of_book =  ("{match}".format(match = match.group()))
                name_of_book=name_of_book.replace('"name">', '')
                name_of_book=name_of_book.replace('&amp;', '&')
                name_of_book=name_of_book.replace('</span>', '')


            regex_author = r"author\">[a-zA-Z\.\s\,]*"
            matches_name = re.finditer(regex_author, text, re.MULTILINE)

            for matchNum, match in enumerate(matches_name, start=1):

                name_of_author=("{match}".format(match = match.group()))
                name_of_author=name_of_author.replace('author\">', '')
                name_of_author=name_of_author.replace('&amp;', '&')
                name_of_author=name_of_author.replace(',', ' ')

            regex_publisher_and_year = r"publisher\">[a-zA-Z\s\W]*[0-9]*"
            matches_publisher_and_year = re.finditer(regex_publisher_and_year, text, re.MULTILINE)

            for matchNum, match in enumerate(matches_publisher_and_year, start=1):
                first_match=("{match}".format(match = match.group()))
                first_match=first_match.replace('publisher\">','')
                first_match=first_match.replace('&amp;', '&')
                first_match= first_match.split(',')
                publisher = first_match[0]
                publication_year = first_match[1]
                publication_year=publication_year.replace(' ', '')

            regex_language = r'lang=\w*'
            matches_language = re.finditer(regex_language, text, re.MULTILINE)

            for matchNum, match in enumerate(matches_language):
                language=("{match}".format(match = match.group()))

            regex_edution = r'bookformat\"/>[a-zA-Z]*'
            matches_edution = re.finditer(regex_edution, text, re.MULTILINE)

            for matchNum, match in enumerate(matches_edution):
                edution=("{match}".format(match = match.group()))
                edution= edution.replace('bookformat\"/>', '')

            info_desciription = html.find_all(class_ = "description")
            info_desciription = (str(info_desciription))
            if len(info_desciription) > 100:
                regex_desciription = r'itemprop=\"description\">.*\.'
                matches_description = re.finditer(regex_desciription, info_desciription, re.MULTILINE)

                for matchNum, match in enumerate(matches_description, start=1):
                    description=("{match}".format(match = match.group()))
                    description= description.replace('itemprop=\"description">', '')
                    description= description.replace('description"><p>', '')
                    description= description.replace('><p>', '')
                    description= description.replace('<strong>', '')
                    description= description.replace('<br/><br/>', '')
                    description= description.replace('</strong></p><p>', '')
                    description= description.replace('</p><p>', '')
                    description= description.replace('</p', '')
            else:
                description = str('No description is available')


            info_rating = html.find_all(class_ = "rating")
            info_rating = (str(info_rating))

            regex_rating = r'book-rating-average text-muted\">[0-9\.]*'
            matches_rating = re.finditer(regex_rating, info_rating, re.MULTILINE)

            for matchNum, match in enumerate(matches_rating, start=1):
                rating=("{match}".format(match = match.group()))
                rating= rating.replace('book-rating-average text-muted\">', '')


            regex_voters = r'book-rating-provider text-muted\">[0-9\s]*'
            matches_voters = re.finditer(regex_voters, info_rating, re.MULTILINE)

            for matchNum, match in enumerate(matches_voters, start=1):
                voters=("{match}".format(match = match.group()))
                voters= voters.replace('book-rating-provider text-muted\">', '')
                voters= voters.replace(' ', '')

            info_number_of_page = html.find_all(class_ = "item-note")
            info_number_of_page = (str(info_number_of_page))

            regex_number_of_pages = r'[0-9\s]*pages'
            matches_number_of_pages = re.finditer(regex_number_of_pages, info_number_of_page, re.MULTILINE)
            matches_number_of_pages_list = []
            for matchNum, match in enumerate(matches_number_of_pages, start=1):
                number_of_pages=("{match}".format(match = match.group()))
                number_of_pages= number_of_pages.replace(' ', '')
                number_of_pages= number_of_pages.replace('pages', '')
                matches_number_of_pages_list.append(number_of_pages)
            number_of_pages= mode(matches_number_of_pages_list)

            print('Please give rating',name_of_book,' between 1 and 5')    
            user_rating = input('Rating: ')

            dict_of_book_info = {"name_of_book": name_of_book,"name_of_author":name_of_author,'publisher':publisher,
                               'publication_year':publication_year,'language': language,'edution': edution,'number_of_pages':number_of_pages,
                               'avg_rating':rating, 'voters':voters,'description':description,'user_rating': user_rating}


            new_user_df = new_user_df.append(dict_of_book_info,ignore_index = True)
        else:
            print(isbn_check,'Do you want to add book manually?')
            manually_adder_decision = input('yes/no')
            if manually_adder_decision == 'yes':
                    name_of_book = input('Enter the name of the book')
                    name_of_author = input('Enter the name of the author')
                    isbn = input('9781781100219')
                    rating = input('Enter the name of the Rating')
                    publication_year = input('Enter the name of the publish_year')
                    publisher = input('Enter the nane of the publisher')
                    description = name_of_book
                    dict_of_book_info = {"name_of_book": name_of_book,"name_of_author":name_of_author,'isbn':isbn,
                                         'publisher':publisher,'publication_year':publication_year, 
                                         'avg_rating':rating,'description':description,'user_rating': rating}


                    new_user_df = new_user_df.append(dict_of_book_info,ignore_index = True)

#%%

a = [1,2,3,4,5]