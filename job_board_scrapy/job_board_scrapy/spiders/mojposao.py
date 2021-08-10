import scrapy
from scrapy import Request
from peewee import *
import pdb

db = SqliteDatabase('mojposao.db')

class Jobbb(Model):

    # id = AutoField()
    db_zupanija = TextField()
    db_mjesto = TextField()
    db_tvrtka = TextField(null = True) # null = True
    db_pozicija = TextField()
    db_vrijedi_do = TextField() # * date_time kasnije (ima modul)
    db_link_za_posao = TextField()

    class Meta:
        database = db

db.connect()
db.create_tables([Jobbb])

class MojposaoSpider(scrapy.Spider):

    name = 'mojposao'
    allowed_domains = ['www.moj-posao.net']

    def start_requests(self):
        url = 'https://www.moj-posao.net/Zupanije/'
        yield Request(url=url, callback=self.parse_start_url)

    def parse_start_url(self, response):
        info = {
            'zupanije':  response.selector.xpath("//div[@class='list']/ul/li/a/text()").extract(),
            'link_zup':  response.selector.xpath("//div[@class='list']/ul/li/a/@href").extract()
            }
        for zup, link in zip(info['zupanije'], info['link_zup']):
            yield Request(
                url=link,
                callback=self.parse,
                cb_kwargs=dict(zupanije=zup[6:])
            )


    def parse(self, response, zupanije):
        for featured_job in response.selector.xpath('//*[@id="featured-jobs"]/ul/li'):
            pozicije = featured_job.xpath('.//*[@class="job-position  "]/text()').extract()
            mjesta = featured_job.xpath('.//*[@class="job-location"]/text()').extract()
            vrijede_do = featured_job.xpath('.//*[@class="deadline"]/text()').extract()
            linkovi_za_poslove = featured_job.xpath('.//*[@class="job-data"]/a/@href').extract()

            for pozicija, mjesta, vrijedi_do, link_za_posao in zip(pozicije, mjesta, vrijede_do, linkovi_za_poslove):
                Jobbb.create(
                    db_zupanija=zupanije,
                    db_mjesto=mjesta,
                    db_tvrtka=featured_job.xpath('.//img[@class="logo"]/@title').extract(),
                    db_pozicija=pozicija.strip(),
                    db_link_za_posao=link_za_posao,
                    db_vrijedi_do=vrijedi_do
                    )


        for job in response.selector.xpath('//*[@class="general-info"]'):
            pozicije = job.xpath('.//*[@class="job-title"]/a/text()').extract()
            for pozicija in pozicije:
               # breakpoint()
                Jobbb.create(
                    db_zupanija=zupanije,
                    db_mjesto=job.xpath('.//*[@class="job-location"]/text()').extract(),
                    db_tvrta=job.xpath('.//*[@class="job-company"]/a/text()').extract() or job.xpath('.//*[@class="job-company"]/text()').extract(),
                    db_pozicija=pozicija.strip(),
                    db_vrijedi_do=job.xpath('.//*[@class="deadline"]/time/text()').extract(),
                    db_link_za_posao=job.xpath('.//*[@class="job-title"]/a/@href').extract()
                    )

        for next_page in response.selector.xpath('*//*[@class="next icon"]/a/@href').extract():
            yield Request(url=next_page, callback=self.parse, cb_kwargs=dict(zupanije=zupanije))


db.close()