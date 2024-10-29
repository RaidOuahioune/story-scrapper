# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv


class MainPipeline:
    def process_item(self, item, spider):
        return item


class HakawatyPipeline:
    def open_spider(self, spider):
        # Open CSV file in write mode
        self.file = open("hakawati.csv", mode="w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        # Write headers to the CSV file
        self.writer.writerow(["title", "content", "age", "value"])

    def close_spider(self, spider):
        # Close the file when the spider is done
        self.file.close()

    def process_item(self, item, spider):
        # Write the data to the CSV file
        for category_name, story_data in item.items():
            title = story_data["title"]  # Title of the story
            story = story_data["content"]  # Story content
            age = category_name  # Use the category name as "age"
            value = ""  # Placeholder for the empty "value" column

            # Write a row to the CSV with four columns
            self.writer.writerow([title, story, age, value])

        return item
