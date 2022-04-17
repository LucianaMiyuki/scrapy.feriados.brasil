# /-----------------------------------------------------------------------------
# / Scrapy: aranha_feriado.py
# / Faz levantamento de todos os feriados das cidades de um determinado Estado.
# / Comando: scrapy crawl -a ano=<ano> -a estado=<sigla>
# /          onde ano é o ano que quer fazer o levantamento e estado é a sigla do
# /          estado do Brasil: ac,al,am,ap,ba,ce,df,es,go,ma,mg,ms,mt,pa,pb,pe,
# /          pi,pr,rj,rn,ro,rr,rs,sc,se,sp,to
# /-----------------------------------------------------------------------------
import scrapy
from datetime import date
import csv 

class FeriadosSpider(scrapy.Spider):

    name = "aranha_feriados"
    start_urls = ['https://www.feriados.com.br/']
    ano = None
    estado = None

    def parse(self, response):
        if self.estado == None:
            print('\n\
            ##########################################  ATENCAO!!!!  ########################################### \n\
            =========> Por favor, digite a sigla de um Estado do Brasil. Ex.: estado=sp ou estado=rj <========== \n\
            ####################################################################################################\n\n')
        else:
            hoje = date.today()
            hoje = hoje.strftime("%Y%m%d")
            self.estado = self.estado.upper() 
            nome_arquivo = 'lista_feriados_' + self.estado + '_' + hoje + '.csv'

            # Cria arquivo de saida com o header
            with open(nome_arquivo, 'a', newline='', encoding="utf-8")  as output_header:
                arq_header = csv.DictWriter(output_header, fieldnames=['ANO', 'ESTADO', 'CIDADE', 'DATA','FERIADO'])       
                arq_header.writeheader()       
            
            # Seleciona os links do site por estado
            estados = response.xpath("//a[contains(@href, 'feriados-estado-')]")
            for est in estados:
                url_est = est.xpath('.//@href').extract_first()
                sigla = url_est[-6:-4]
                sigla = sigla.upper() 

                # Para o estado escolhido na execução do processo, seleciona o link correspondente
                if sigla == self.estado:
                    yield scrapy.Request(
                        url = 'https://www.feriados.com.br/%s' % url_est,
                        callback=self.parse_cidades
                    )

    # Para cada cidade do estado escolhido, lista todos os links
    def parse_cidades(self, response):    
        hrefs = response.xpath("//a[contains(@href, 'feriados')]")
        for link in hrefs:
            url = link.xpath('.//@href').extract_first()
            if 'http://www.feriados.com.br/feriados' in url:
                url = url + '?ano=' + self.ano 
 
                yield scrapy.Request(
                    url,
                    callback=self.parse_feriados
                )

    # Para cada uma das cidades, lista as informações dos feriados
    def parse_feriados(self, response):
        feriado_ano = response.xpath("//*[@id='location_header']/a[1]/text()").extract_first()
        ano = feriado_ano[9:13]

        cidade = response.xpath("//*[@id='location_header']/a[2]/text()").extract_first()
        cidade = cidade.title()

        dias  = response.xpath("//div[contains(@id, cidade)]/ul/li/div")

        url_estado = response.xpath("//*[@id='location_header']/a[2]")
        url_estado = url_estado.xpath(".//@href").extract_first()

        estado = url_estado[-6:-4]
        estado = estado.upper()

        for dia in dias:
            dia_feriado = dia.xpath('.//span/text()').extract_first()
            tamanho = len(dia_feriado)
            data_feriado = dia_feriado[0:10]
            descricao = dia.xpath('.//a/text()').extract_first()

            if descricao == None:
                descricao = dia_feriado[13:50]
            descricao = descricao.title()  

            post = {
                'ano': ano,
                'estado': estado,
                'cidade': cidade,
                'data_feriado': data_feriado,
                'descricao': descricao
            }

            hoje = date.today()
            hoje = hoje.strftime("%Y%m%d")
            self.estado = self.estado.upper()
            nome_arquivo = 'lista_feriados_' + self.estado + '_' + hoje + '.csv'

            with open(nome_arquivo, 'a', newline='', encoding="utf-8")  as output_file:
                dict_writer = csv.DictWriter(output_file, post.keys())       
                dict_writer.writerows([post])        
            yield post