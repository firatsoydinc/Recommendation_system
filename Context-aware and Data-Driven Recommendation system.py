#!/usr/bin/env python
# coding: utf-8

# ### Content-Based Recommendation System with Real Dataset
# 
# Distance is an important variable since the process of borrowing books from the pop-up library is done physically. During the user testing with the online dataset, the participants thought that it was not helpful to recommend a book located far away. For this reason, it has been tried to make accessible recommendations to the user by adding the city restriction to the study.
# 
# By determining the pop-up libraries in Utrecht, Netherlands as the pilot region for the study, a recommendation system was developed by using the books in these pop-up libraries.
# 
# The data of the books in the pop-up libraries in Utrecht were obtained by web scraping using bookfinder.com over the ISBN number.
# 
# The methods used in the recommendation system such as web scraper and geofinder are detailed in the file important_functions.py.

# In[1]:


import pandas as pd 
import requests
from bs4 import BeautifulSoup
import re

import pgeocode
import geopy.distance
import geocoder

from statistics import mode

## To calculate cosine similarity among books 
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer

import warnings
warnings.filterwarnings("ignore")


# In[2]:


def recommendation_system():
    user_name = input('Please enter your name:')
    print('Welcome', user_name,'Do you want to share your current location with us to give you better recommendations?')
    ## User's location sharing preferences
    user_preferences_1 = input('Yes/No? ')
    if ((user_preferences_1.lower() == 'yes')|(user_preferences_1.lower() == 'y')):
        ##Accessing location data using IP address
            geocode  = geocoder.ip('me')
            latitude = geocode.latlng[0]
            longitude= geocode.latlng[1]
    else:
        ##Accessing location data using postal code
        nomi = pgeocode.Nominatim('nl')
        postal_code = input('Please enter your current postal code')
        postal_code= str(postal_code)
        a = nomi.query_postal_code(postal_code)
        a = a.to_frame().reset_index()
        geo_codes = a[(a['index'] == 'latitude') | (a['index'] == 'longitude')]
        geo_codes.reset_index(drop= True, inplace=True)
        geo_codes=geo_codes.rename(columns={'index':'geotype',0:'geo_number'})
        geo_codes["geo_number"] = pd.to_numeric(geo_codes["geo_number"], downcast="float")
        latitude = geo_codes[0:1]
        longitude= geo_codes[1:2]
        latitude =latitude['geo_number'][0]
        longitude = longitude['geo_number'][1]
    print('Do you want to enter your favorite books to start taking recommendations?')
    user_preferences_2 = input('Yes/No: ')
    if ((user_preferences_2.lower() == 'yes')|(user_preferences_2.lower() == 'y')):
        ##Saving the ISBN of the books that the user wants to add to the system
        isbn_list = [] 
        isbn_number = input('Please enter ISBN number of your book: ')
        isbn_list.append(isbn_number)
        q = input  ("Do you want to write another ISBN number? Yes/No ")
        q=q.lower()
        while ((q == 'yes')|(q=='y')):
            if (q.lower() =='y') | (q.lower()== 'yes'):
                isbn = input ("Please enter isbn number of the book: ")
                isbn_list.append(isbn)
                q = input  ("Do you want to write another isbn number? ")

        print(isbn_list)
        new_user_df = pd.DataFrame()
        all_languages = []
        ## Web scraper scraps book metadata from bookfinder.com
        for each_isbn in isbn_list:

            base_url = 'https://www.bookfinder.com/search/?isbn='+each_isbn+'&mode=isbn&st=sr&ac=qr'
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
                lang_list= []
                for matchNum, match in enumerate(matches_language):
                    language=("{match}".format(match = match.group()))
                    language = language.replace('lang=', '')
                    lang_list.append(language)
                language=lang_list[0]
                all_languages.append(language)

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
                        description= description.replace('<p>', '')
                        description= description.replace('<br/>', '')
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

                dict_of_book_info = {"Name": name_of_book,"Authors":name_of_author,'Publisher':publisher,
                                   'ISBN':each_isbn, 'PublishYear':publication_year,'new_lang': language,'edution': edution,
                                   'avg_rating':rating, 'voters':voters,'description':description}


                new_user_df = new_user_df.append(dict_of_book_info,ignore_index = True)
            else:
                print(isbn_check,'Do you want to add book manually?')
                manually_adder_decision = input('yes/no')
                if manually_adder_decision == 'yes':
                        name_of_book = input('Enter the name of the book')
                        name_of_author = input('Enter the name of the author')
                        isbn = input('Enter ISBN number of the book')
                        rating = input('Enter the name of the Rating')
                        publication_year = input('Enter the name of the publish_year')
                        publisher = input('Enter the name of the publisher')
                        language = input('Enter the language of the language')
                        avg_rating = rating
                        description = name_of_book
                        dict_of_book_info = {"Name": name_of_book,"Authors":name_of_author,'ISBN':isbn,
                                             'Publisher':publisher,'PublishYear':publication_year,'new_lang': language,
                                             'avg_rating':rating,'description':description,}


                        new_user_df = new_user_df.append(dict_of_book_info,ignore_index = True)

            coords_user= (latitude,longitude)
            df_books_and_geocodes = pd.read_csv(r'cleaned_and_scraped_real_data.csv')
            df_books_and_geocodes['distance'] = ''
            for index, each in enumerate(df_books_and_geocodes.Geocode):
                df_books_and_geocodes['distance'][index] = geopy.distance.geodesic(coords_user, each).km

            df_bookss = pd.concat([df_books_and_geocodes,new_user_df])
            df_bookss.reset_index(drop=True,inplace=True)

            tf = TfidfVectorizer(analyzer='word',
                         ngram_range=(1, 2),
                         min_df=0)

            tfidf_matrix = tf.fit_transform(df_bookss['description'])

            ## Calculate cosine similarity of the books descriprion
            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

            ## create dataframe with Name, Author, PublishYear, Publisher, new_lang, Description
            titles = df_bookss[['Name','ISBN', 'Adress','new_lang','description','Geocode']]

            ## Save the name of the books as an index
            indices = pd.Series(df_bookss.index, index=df_bookss['ISBN'])
            try:
            # handle case in which book by same title is in dataset
                idx = indices[each_isbn][0]
            except IndexError:
                idx = indices[each_isbn]

            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:]
            # There is an exact match between books with missing description data. 
            # These books have been removed from the dataset.
            new_sim_scores= []
            for each in sim_scores:
                if each[1]!= 1:
                    new_sim_scores.append(each)
                    
            book_indices = [i[0] for i in new_sim_scores]
            book_sim_ratio = [i[1] for i in new_sim_scores]
            book_sim_ratio_cols = {"book_index": book_indices,"book_sim_ratio":book_sim_ratio}
            book_sim_ratio_df = new_user_df.append(book_sim_ratio_cols,ignore_index = True) 
            
            df_bookss = df_bookss.rename(columns={'Unnamed: 0' :'indices' })
            book_sim_ratio_df = pd.DataFrame.from_records(new_sim_scores, columns =['indices', 'sim_scores'])
            
            recommendation = df_bookss.merge(book_sim_ratio_df,how='inner',on='indices')
            new_cols= ['Name', 'ISBN', 'Adress', 'new_lang', 'description', 'Geocode','sim_scores']
            recommendation = recommendation [new_cols]
            
            language_based_list = pd.DataFrame()
            for lang in all_languages:
                a = recommendation[recommendation['new_lang'] == lang]
                language_based_list = language_based_list.append(a)

            coords_user= (latitude,longitude)
            language_based_list['distance'] = ''
            language_based_list = language_based_list.dropna(subset=['Geocode'])
            language_based_list = language_based_list.reset_index(drop=True)
            for index, each in enumerate(language_based_list.Geocode):
                language_based_list['distance'][index]= geopy.distance.geodesic(coords_user, each).km

            language_based_list_cols = ['Name','ISBN','new_lang','distance','Adress','sim_scores']
            language_based_list = language_based_list[language_based_list_cols]
            ## Removing the books which have no similarity from the user book
            language_based_list = language_based_list[language_based_list.sim_scores>0]

            print('The books given by user is written in',set(all_languages),'. So only',set(all_languages), 'books are shown in the recommendation')
            print('1: Distance')
            print('2: Similarity')

            user_input = input('How do you want to sort your recommendations?')
            if user_input == '1':
                print('####### Nearest books ##########')
                print(language_based_list.sort_values(by='distance',ascending= False).head(5))
            else:
                print('####### Most Similar books ##########')
                print(language_based_list.sort_values(by='sim_scores',ascending= False).head(5))




# In[3]:


recommendation_system()


# In[ ]:




