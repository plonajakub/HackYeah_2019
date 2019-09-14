import json


class Profiler:

    def __init__(self):
        # JSONs
        self.user_history = None
        self.articles = None

    def parse_jsons(self, path_user_history, path_articles):
        """Fills user_history and articles with data"""
        with open(path_user_history) as f:
            self.user_history = json.load(f)
            print(self.user_history)    #Debug

        with open(path_articles) as f:
            self.articles = json.load(f)
            print(self.articles)    #Debug

    def create_tag_distribution_from_user_history(self):
        """Counts tags in user_history"""
        tag_dictionary = {}
        return tag_dictionary

    def find_matching_articles(self, tag_distribution):
        """Searches for best matched articles comparing tags"""
        articles_url = []
        return articles_url

    def print_matching_articles_urls(self, articles_url):
        """Export URLs for matched articles to the STDOUT"""
        print(articles_url)

    def run(self, path_user_history, path_articles):
        """Algorithm"""
        self.parse_jsons(path_user_history, path_articles)
        tag_distribution = self.create_tag_distribution_from_user_history()
        articles_url = self.find_matching_articles(tag_distribution)
        self.print_matching_articles_urls(articles_url)

