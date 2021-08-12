import scrapy
from scrapy import Request
from peewee import *
import datetime

db = SqliteDatabase("poslovi.db")


class MojPosao(Model):

    zupanija = TextField()
    mjesto = TextField()
    tvrtka = TextField()
    pozicija = TextField()
    vrijedi_do = TextField()
    link_za_posao = TextField()
    datum_prikupljanja = DateField()

    class Meta:
        database = db


db.connect()
db.create_tables([MojPosao])


class MojposaoSpider(scrapy.Spider):

    name = "mojposao"
    allowed_domains = ["www.moj-posao.net"]

    def start_requests(self):
        url = "https://www.moj-posao.net/Zupanije/"
        yield Request(url=url, callback=self.parse_start_url)

    def parse_start_url(self, response):
        info = {
            "zupanije": response.selector.xpath(
                "//div[@class='list']/ul/li/a/text()"
            ).extract(),
            "link_zup": response.selector.xpath(
                "//div[@class='list']/ul/li/a/@href"
            ).extract(),
        }
        for zup, link in zip(info["zupanije"], info["link_zup"]):
            yield Request(
                url=link, callback=self.parse, cb_kwargs=dict(zupanije=zup[6:])
            )

    def parse(self, response, zupanije):
        j_datum_prikupljanja = datetime.date.today()

        for featured_job in response.selector.xpath('//*[@id="featured-jobs"]/ul/li'):
            pozicije = featured_job.xpath(
                './/*[@class="job-position  "]/text()'
            ).extract()
            j_mjesta = featured_job.xpath(
                './/*[@class="job-location"]/text()'
            ).extract()
            vrijede_do = featured_job.xpath('.//*[@class="deadline"]/text()').extract()
            linkovi_za_poslove = featured_job.xpath(
                './/*[@class="job-data"]/a/@href'
            ).extract()

            for j_pozicija, j_mjesta, j_vrijedi_do, j_link_za_posao in zip(
                pozicije, j_mjesta, vrijede_do, linkovi_za_poslove
            ):
                j_tvrtka = featured_job.xpath('.//img[@class="logo"]/@title').extract()[
                    0
                ]
                j_pozicija = j_pozicija.strip()

                MojPosao.create(
                    zupanija=zupanije,
                    mjesto=j_mjesta,
                    tvrtka=j_tvrtka,
                    pozicija=j_pozicija,
                    link_za_posao=j_link_za_posao,
                    vrijedi_do=j_vrijedi_do,
                    datum_prikupljanja=j_datum_prikupljanja
                )

                yield {
                    "Zupanija": zupanije,
                    "Mjesto": j_mjesta,
                    "Tvrtka": j_tvrtka,
                    "Pozicija": j_pozicija,
                    "Vrijedi_do": j_vrijedi_do,
                    "Link_za_posao": j_link_za_posao,
                }

        for job in response.selector.xpath('//*[@class="general-info"]'):
            pozicije = job.xpath('.//*[@class="job-title"]/a/text()').extract()
            for j_pozicija in pozicije:
                j_pozicija = j_pozicija.strip()
                j_mjesto = job.xpath('.//*[@class="job-location"]/text()').extract()
                j_vrijeme = job.xpath('.//*[@class="deadline"]/time/text()').extract()
                j_link = job.xpath('.//*[@class="job-title"]/a/@href').extract()
                j_tvrtka = (
                    job.xpath('.//*[@class="job-company"]/a/text()').extract()
                    or job.xpath('.//*[@class="job-company"]/text()').extract()
                )

                if type(j_mjesto) == list:
                    j_mjesto = j_mjesto[0]
                if type(j_tvrtka) == list:
                    j_tvrtka = j_tvrtka[0]
                if type(j_vrijeme) == list:
                    j_vrijeme = j_vrijeme[0]
                if type(j_link) == list:
                    j_link = j_link[0]

                yield {
                    "Zupanija": zupanije,
                    "Mjesto": j_mjesto,
                    "Tvrtka": j_tvrtka,
                    "Pozicija": j_pozicija,
                    "Vrijedi_do": j_vrijeme,
                    "Link_za_posao": j_link,
                }

                MojPosao.create(
                    zupanija=zupanije,
                    mjesto=j_mjesto,
                    tvrtka=j_tvrtka,
                    pozicija=j_pozicija,
                    vrijedi_do=j_vrijeme,
                    link_za_posao=j_link,
                    datum_prikupljanja=j_datum_prikupljanja
                )

        for next_page in response.selector.xpath(
            '*//*[@class="next icon"]/a/@href'
        ).extract():
            yield Request(
                url=next_page, callback=self.parse, cb_kwargs=dict(zupanije=zupanije)
            )


db.close()
