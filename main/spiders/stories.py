import scrapy

class StorySpider(scrapy.Spider):
    name = "story"
    
    # The URL(s) you want to scrape
    start_urls = ['https://www.storyberries.com/bedtime-stories-elvis-big-adventure-short-stories-for-kids/']
    
    def parse(self, response):
        # Saving the HTML of the page
        page = response.url.split("/")[-2]
        filename = f'story-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        
        self.log(f'Saved file {filename}')
