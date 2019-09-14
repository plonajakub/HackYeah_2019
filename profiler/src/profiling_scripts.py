import json
import operator


class Profiler:

    def __init__(self):
        # JSONs
        self.user_history = None
        self.articles = None

    def parse_jsons(self, path_user_history, path_articles):
        """Fills user_history and articles with data"""
        with open(path_user_history) as f:
            self.user_history = json.load(f)
            # print(self.user_history)  # Debug

        with open(path_articles) as f:
            self.articles = json.load(f)
            # print(self.articles)  # Debug

    def create_tag_distribution_from_user_history(self):
        """Counts tags in user_history"""
        tag_dictionary = {}
        for visited_site in self.user_history['user_history']['visited_sites']:
            for tag in visited_site['tags']:
                if tag not in tag_dictionary:
                    tag_dictionary[tag] = 0
                tag_dictionary[tag] = tag_dictionary[tag] + 1
        return tag_dictionary

    def find_matching_articles(self, tag_distribution):
        """Searches for best matched articles comparing tags"""

        articles_score = {}
        for article in self.articles['articles']:
            articles_score[article['url']] = 0
            for tag_occurrence_pair in tag_distribution.items():
                if tag_occurrence_pair[0] in article['tags']:
                    if type(article['tags']) is dict:
                        articles_score[article['url']] += tag_occurrence_pair[1] * article['tags'][
                            tag_occurrence_pair[0]]
                    else:
                        articles_score[article['url']] += tag_occurrence_pair[1]

        sorted_articles_by_score = sorted(articles_score.items(), key=operator.itemgetter(1), reverse=True)

        articles_url = []
        for article_score_pair in sorted_articles_by_score:
            articles_url.append(article_score_pair[0])

        return articles_url

    def print_matching_articles_urls(self, articles_url):
        """Export URLs for matched articles to the STDOUT"""
        match_result = {'user_id': self.user_history['user_history']['user_id'], 'sorted_urls': []}
        for url in articles_url:
            match_result['sorted_urls'].append(url)
        print(str(match_result).replace("\'", "\""))

    def run(self, path_user_history, path_articles):
        """Algorithm"""
        self.parse_jsons(path_user_history, path_articles)
        tag_distribution = self.create_tag_distribution_from_user_history()
        articles_url = self.find_matching_articles(tag_distribution)
        self.print_matching_articles_urls(articles_url)
