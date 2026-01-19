# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class FacultyItem(scrapy.Item):
    name = scrapy.Field()
    profile_url = scrapy.Field()
    education = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()
    address = scrapy.Field()
    biography = scrapy.Field()
    specialization = scrapy.Field()
    teaching = scrapy.Field()
    faculty_web = scrapy.Field()
    research = scrapy.Field()
    publications = scrapy.Field()