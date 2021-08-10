import scrapy
from scrapy import Request
from peewee import *
import datetime

db = SqliteDatabase('posao_hr.db')

class Posao(Model):

    zupanija = TextField()
    mjesto = TextField()
    tvrtka = TextField()
    pozicija = TextField()
    vrijedi_do = TextField()
    link_za_posao = TextField()

    class Meta:
        database = db

db.connect()
db.create_tables([Posao])


class PosaoSpider(scrapy.Spider):

    name = 'posao'
    allowed_domains = ['www.posao.hr']


    def start_requests(self):
        url = 'https://www.posao.hr'
        yield Request(url=url, callback=self.parse_start_url)


    def parse_start_url(self, response):
        info = {
            'zupanije':  response.selector.xpath('//*[@class="districts"]/ul/li/a/text()').extract(),
            'link_zup':  response.selector.xpath('//*[@class="districts"]/ul/li/a/@href').extract()
            }
        for zup, link in zip(info['zupanije'], info['link_zup']):
            yield Request(
                url=link,
                callback=self.parse,
                cb_kwargs=dict(zupanije=zup, first_page=True)
                )


    def parse(self, response, zupanije, first_page):
        for special_job in  response.selector.xpath('//div[@class="intro"]'):
            sj_mjesto = special_job.xpath('./a/div/div/span/text()').extract()[0]
            sj_tvrtka = special_job.xpath('../div/a/img/@alt').extract()[0]
            sj_pozicija = special_job.xpath('./a/strong/text()').extract()
            sj_link_za_posao = special_job.xpath('./a/@href').extract()

            dani_do_isteka = special_job.xpath('./a/div/div/span/text()').extract()[1]
            try:
                sj_vrijedi_do_posao = datetime.date.today() + datetime.timedelta(days=int((dani_do_isteka.split()[0])))
            except:
                pass
            if type(sj_pozicija) == list:
                sj_pozicija = sj_pozicija[0]
            if type(sj_link_za_posao) == list:
                sj_link_za_posao = sj_link_za_posao[0]

            Posao.create(
                zupanija=zupanije,
                mjesto=sj_mjesto,
                tvrtka=sj_tvrtka,
                pozicija= sj_pozicija,
                link_za_posao=sj_link_za_posao,
                vrijedi_do=sj_vrijedi_do_posao
                )

            yield {
                'Zupanija': zupanije,
                'Mjesto': sj_mjesto,
                'Tvrtka': sj_tvrtka,
                'Pozicija': sj_pozicija,
                'Vrijedi_do': sj_vrijedi_do_posao,
                'Link_za_posao': sj_link_za_posao
                }

        if first_page == True:
            j_tvrtke = response.selector.xpath('//table//div[@class="employer res_date_time_comp"]/text()').extract() +  response.selector.xpath('//table//div[@class="company employer res_date_time_comp"]/text()').extract()
            j_pozicije = response.selector.xpath('//table//div[@class="title"]/text()').extract()  +  response.selector.xpath('//table//div[@class="normal_title title"]/text()').extract()
        else:
            j_tvrtke = response.selector.xpath('//table//div[@class="employer res_date_time_comp"]/text()').extract() or  response.selector.xpath('//table//div[@class="company employer res_date_time_comp"]/text()').extract()
            j_pozicije = response.selector.xpath('//table//div[@class="title"]/text()').extract()  or  response.selector.xpath('//table//div[@class="normal_title title"]/text()').extract()

        j_mjesta = response.selector.xpath('//table//div[@class="location res_date_time_comp"]/text()').extract()
        j_datumi = response.selector.xpath('//table//div[@class="deadline res_date_time_comp"]/text()').extract()
        j_linkovi_za_poslove = response.selector.xpath('//table//a/@href').extract()

        for j_mjesto, j_tvrtka, j_pozicija, j_datum, j_link in zip(j_mjesta, j_tvrtke, j_pozicije, j_datumi, j_linkovi_za_poslove):
            try:
                j_datum = datetime.date.today() + datetime.timedelta(days=int((j_datum.split()[0])))
            except:
                pass
            if type(j_pozicija) == list:
                j_pozicija = j_pozicija[0]
            if type(j_link) == list:
                j_link= j_link[0]

            Posao.create(
                zupanija=zupanije,
                mjesto=j_mjesto,
                tvrtka=j_tvrtka,
                pozicija= j_pozicija,
                link_za_posao=j_link,
                vrijedi_do=j_datum
                )

            yield {
                'Zupanija': zupanije,
                'Mjesto': j_mjesto,
                'Tvrtka': j_tvrtka,
                'Pozicija': j_pozicija,
                'Vrijedi_do': j_datum,
                'Link_za_posao': j_link
                }

        next_page = response.selector.xpath('*//span[@class="pages"]/a/@href').extract()
        yield Request(url=next_page[-2], callback=self.parse, cb_kwargs=dict(zupanije=zupanije, first_page=False))
