from enum import unique
from requests import get
from bs4 import BeautifulSoup
import csv
import re
import string
import math
url = 'https://www.imdb.com/title/tt1837492/episodes?season={}&ref_=tt_eps_sn_{}'
list_reviews = []
list_words = []

class Review():

    def __init__(self, episode_name, text, score):
        self.episode_name = episode_name
        self.text = f"\n{text.lower()}\n"
        self.score = int(score)
        self.status = ''
        self.set_review_status()

    def set_review_status(self):
        self.status = 'negative' if self.score < 8 else 'positive'

class Word():

    def __init__(self, word, review_number, review_status, positive_frequency = 0, negative_frequency = 0, positive_reviews = 0, negative_reviews = 0):
        self.text = word
        self.review_number = review_number
        self.review_status = review_status
        self.positive_frequency = positive_frequency
        self.negative_frequency = negative_frequency
        self.positive_reviews = positive_reviews
        self.negative_reviews = negative_reviews
        self.positive_probability = 0
        self.negative_probability = 0 
        if self.negative_frequency == 0 and self.positive_frequency == 0:
            if self.review_status == "positive":
                self.positive_frequency += 1
                self.positive_reviews += 1
            else:
                self.negative_frequency += 1
                self.negative_reviews += 1

    def __eq__(self, other):
        if other != None and self.text == other.text:
            return True
        return False

    def set_review_number(self, review_number):
        self.review_number = review_number
    
    def set_positive_probability(self, positive_probability):
        self.positive_probability = positive_probability
    
    def set_negative_probability(self, negative_probability):
        self.negative_probability = negative_probability

    def increment_reviews(self, review_number, review_status):
        if self.review_number != review_number:
            self.review_number = review_number
            if review_status == 'positive':
                self.positive_reviews += 1
            else:
                self.negative_reviews += 1

    def increment_frequency(self, review_status):
        if review_status == "positive":
            self.positive_frequency += 1
        else:
            self.negative_frequency += 1

def remove_emoji(list_words, return_list, positive_words = 0, negative_words = 0):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    for word in list_words:
        if emoji_pattern.sub(r'', word.text) != '':
            return_list.append(Word(emoji_pattern.sub(r'', word.text),word.review_number, word.review_status,positive_frequency =  word.positive_frequency, negative_frequency = word.negative_frequency, positive_reviews=word.positive_reviews, negative_reviews=word.negative_reviews))
    return return_list
def search_list(list_words, text):
    for word in list_words:
        if word.text == text:
            return word
    return None

with open('data.csv', 'w', newline='') as file:
    field_names = ['Name', 'Season', 'Review Link', 'Year']
    writer = csv.DictWriter(file, fieldnames = field_names)
    writer.writeheader()
    for x in range(1,5,1):
        response = get(url.format(x, x))
        html_soup = BeautifulSoup(response.text, 'html.parser')
        episodesContainerOdd = html_soup.find_all('div', class_ = 'list_item odd')
        episodesContainerEven = html_soup.find_all('div', class_ = 'list_item even')
        firstEpisode = episodesContainerOdd[0]
        review_link = "https://www.imdb.com{}reviews?ref_=tt_urv"
        secondEpisode = episodesContainerEven[0]
        for i in range(len(episodesContainerOdd)):
            writer.writerow({'Name': episodesContainerOdd[i].strong.text, 'Season': x, 'Review Link': review_link.format(episodesContainerOdd[i].strong.a['href']), 'Year': episodesContainerOdd[i].find('div', class_ = 'airdate').text.split(" ")[14].split("\n")[0]})
            if i < len(episodesContainerEven):
                writer.writerow({'Name': episodesContainerEven[i].strong.text, 'Season': x, 'Review Link': review_link.format(episodesContainerEven[i].strong.a['href']), 'Year': episodesContainerEven[i].find('div', class_ = 'airdate').text.split(" ")[14].split("\n")[0]})
positive_reviews = []
negative_reviews = []
with open('data.csv', 'r', newline='') as file:
    reader = csv.DictReader(file)
    i = 1
    for row in reader:
        review_link = row['Review Link']
        episode_name = row['Name']
        response = get(review_link)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        ratings = html_soup.find_all('span', class_ = 'rating-other-user-rating')
        reviews = html_soup.find_all('div', class_ = 'lister-item-content')
        ratings_it = 0
        for review in reviews:
            ratings_exist = review.find('span', class_ = 'rating-other-user-rating')
            if ratings_exist == None:
                continue
            review_text = review.find('div', class_ = 'text show-more__control').text
            score = ratings[ratings_it].span.text
            full_review = Review(episode_name, review_text, score)
            positive_reviews.append(full_review) if full_review.status == 'positive' else negative_reviews.append(full_review)
            list_reviews.append(full_review)
            ratings_it += 1
            i += 1
review_number = 1
positive_words = 0
negative_words = 0
for i in range(int(len(positive_reviews)/2)):
    review = positive_reviews[i]
    words = re.sub('['+string.punctuation+']', '', review.text).split()
    for word in words:
        search_result = search_list(list_words, word)
        if search_result != None:
            search_result.increment_frequency(review.status)
            search_result.increment_reviews(review_number, review.status)
        else:
            list_words.append(Word(word, review_number, review.status))
    review_number += 1
pr_number = review_number-1
review_number = 1
for i in range(int(len(negative_reviews)/2)):
    review = negative_reviews[i]
    words = re.sub('['+string.punctuation+']', '', review.text).split()
    for word in words:
        search_result = search_list(list_words, word)
        if search_result != None:
            search_result.increment_frequency(review.status)
            search_result.increment_reviews(review_number, review.status)
        else:
            list_words.append(Word(word, review_number, review.status))
    review_number += 1
nr_number = review_number-1
total_md_review = nr_number + pr_number
positive_words = 0
negative_words = 0
no_emoji_list = remove_emoji(list_words, [])
removed_list = []
for word in no_emoji_list:
    if word.positive_frequency + word.negative_frequency < 3 or word.positive_frequency + word.negative_frequency > 150:
        removed_list.append(word)
    else:
        positive_words += word.positive_frequency
        negative_words += word.negative_frequency
for word in removed_list:
    no_emoji_list.remove(word)
no_emoji_list.sort(key=lambda word: word.text, reverse=False)
removed_list.sort(key=lambda word: word.text, reverse=False)
num_words = 1
smoothing_factor = 1
prediction_correctness = 0
with open('model.txt', 'w', newline='') as file:
    for word in no_emoji_list:
        word.set_positive_probability((word.positive_frequency+smoothing_factor)/(positive_words+(smoothing_factor*len(no_emoji_list))))
        word.set_negative_probability((word.negative_frequency+smoothing_factor)/(negative_words+(smoothing_factor*len(no_emoji_list))))
        file.write(f"Word #{num_words}: {word.text}\nPositive frequency: {word.positive_frequency}, Negative frequency: {word.negative_frequency}\nPositive reviews: {word.positive_probability}, Negative reviews: {word.negative_probability}\n\n")
        num_words += 1
num_words = 1
with open('remove.txt', 'w', newline='') as file:
    for word in removed_list:
        file.write(f"{word.text}\nPositive frequency: {word.positive_frequency}, Negative frequency: {word.negative_frequency}\n\n")
        num_words += 1
total_test_review = 0
with open('result.txt', 'w', newline='') as file:
    for i in range(pr_number, int(len(positive_reviews)), 1):
        positive_probability = math.log10(pr_number/total_md_review)
        negative_probability = math.log10(nr_number/total_md_review)
        review = positive_reviews[i]
        words = re.sub('['+string.punctuation+']', '', review.text).split()
        for word in words:
           search_word = search_list(no_emoji_list, word)
           if search_word != None:
               positive_probability += math.log10(search_word.positive_probability)
               negative_probability += math.log10(search_word.negative_probability)
        result = "positive" if positive_probability >= negative_probability else "negative"
        prediciton_result = "right" if result == review.status else "wrong"
        if prediciton_result == "right":
            prediction_correctness += 1
        total_test_review += 1
        file.write(f"Review: {review.episode_name}\nPositive frequency: {positive_probability}, Negative frequency: {negative_probability} \nPrediction: {result} Review Status {review.status} Correct: {prediciton_result} \n\n")
    for i in range(pr_number, int(len(positive_reviews)), 1):
        positive_probability = math.log10(pr_number/total_md_review)
        negative_probability = math.log10(nr_number/total_md_review)
        review = negative_reviews[i]
        words = re.sub('['+string.punctuation+']', '', review.text).split()
        for word in words:
            search_word = search_list(no_emoji_list, word)
            if search_word != None:
                positive_probability += math.log10(search_word.positive_probability)
                negative_probability += math.log10(search_word.negative_probability)
        result = "positive" if positive_probability >= negative_probability else "negative"
        prediciton_result = "right" if result == review.status else "wrong"
        if prediciton_result == "right":
            prediction_correctness += 1
        total_test_review += 1
        file.write(f"Review: {review.episode_name}\nPositive frequency: {positive_probability}, Negative frequency: {negative_probability} \nPrediction: {result} Review Status {review.status} Correct: {prediciton_result} \n\n") 
    file.write(f"The prediciton correctness is: {(prediction_correctness*100)/total_test_review}")