import scrapy

import html2text
text_maker = html2text.HTML2Text() 
text_maker.ignore_emphasis = True 
text_maker.ignore_images = True 
text_maker.ignore_links = True
text_maker.BODY_WIDTH = 0 

class FaqExtractor(scrapy.Spider):
    name = 'FaqExtractor'
    start_urls = ['https://www.certisign.com.br/duvidas-suporte/perguntas-frequentes/']

    def parse(self, response):
        categoriesUrl = response.css('.roundItems.opcoes4 li a::attr(href)').getall()
        
        for cUrl in categoriesUrl:
            yield scrapy.Request(response.urljoin(cUrl), callback=self.extractFaqs)

    def extractFaqs(self, response):
        questions = response.css('.faqQuestion.accordin::text').getall() 
        answers = self.extractAnswers(response)

        for question, answer in zip(questions, answers):
            if len(answer.split()) <= 500:
                yield {
                    'index_name': 'certisign',
                    'items': answer,
                }


    def extractAnswers(self, response):
        divAnswers = response.css('.divAnswer') 
        answers = [] 
        for self.divAnswer in divAnswers: 
            html = self.getHtml()
            answer = text_maker.handle(html) 
            answer = self.separateTextCorrectly(answer)
            answer = answer.lower()
            answers.append(answer)
        return answers

    def getHtml(self):
        html = self.divAnswer.get() 
        html = html.replace('<br>', 'JUMP') # to replace with '\n' after
        return html

    def separateTextCorrectly(self, text):
        newText = ''
        text = text.strip()
        text = text.replace('\n\n', 'BREAK').replace('\n', ' ').replace('BREAK', '\n\n') # some little breaks
        for separated in text.split('\n\n'):
            separated = separated.replace('\n', '')
            newText += separated + '\n\n'
        newText = newText.replace('JUMP', '\n')
        return newText.rstrip()
