import scrapy
from scrapy import Request

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
            yield {
                'Zupanija': zupanije,
                'Mjesto': special_job.xpath('./a/div/div/span/text()').extract()[0],
                'Tvrtka': special_job.xpath('../div/a/img/@alt').extract()[0],
                'Pozicija': special_job.xpath('./a/strong/text()').extract(),
                'Vrijedi_do': special_job.xpath('./a/div/div/span/text()').extract()[1],
                'Link_za_posao': special_job.xpath('./a/@href').extract()
                }

        if first_page == True:
            tvrtke = response.selector.xpath('//table//div[@class="employer res_date_time_comp"]/text()').extract() +  response.selector.xpath('//table//div[@class="company employer res_date_time_comp"]/text()').extract()
            pozicije = response.selector.xpath('//table//div[@class="title"]/text()').extract()  +  response.selector.xpath('//table//div[@class="normal_title title"]/text()').extract()
        else:
            tvrtke = response.selector.xpath('//table//div[@class="employer res_date_time_comp"]/text()').extract() or  response.selector.xpath('//table//div[@class="company employer res_date_time_comp"]/text()').extract()
            pozicije = response.selector.xpath('//table//div[@class="title"]/text()').extract()  or  response.selector.xpath('//table//div[@class="normal_title title"]/text()').extract()

        mjesta = response.selector.xpath('//table//div[@class="location res_date_time_comp"]/text()').extract()
        datumi = response.selector.xpath('//table//div[@class="deadline res_date_time_comp"]/text()').extract()
        linkovi_za_poslove = response.selector.xpath('//table//a/@href').extract()

        for mjesto, tvrtka, pozicija, datum, link in zip(mjesta, tvrtke, pozicije, datumi, linkovi_za_poslove):
            yield {
                'Zupanija': zupanije,
                'Mjesto': mjesto,
                'Tvrtka': tvrtka,
                'Pozicija': pozicija,
                'Vrijedi_do': datum,
                'Link_za_posao': link
                }

        next_page = response.selector.xpath('*//span[@class="pages"]/a/@href').extract()
        yield Request(url=next_page[-2], callback=self.parse, cb_kwargs=dict(zupanije=zupanije, first_page=False))
