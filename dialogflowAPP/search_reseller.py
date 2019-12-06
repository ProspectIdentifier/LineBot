import requests
from decouple import config
from linebot.models import (CarouselTemplate, TemplateSendMessage,
                            CarouselColumn, URIAction, PostbackAction,
                            MessageAction, TextSendMessage)

# 'Address', 'Blocked', 'RecordType', 'Phone', 'Email', 'PostCode'
titles = ['NavisionID', 'City']
data = ['Address', 'Phone', 'Email', 'PostCode']

def search_reseller(keyword, country):
    r = requests.get(config('RESELLER') % (country, keyword))
    res = r.json()
    return res['Results']

def make_carousel_object(result):
    carousel_list = []

    for item in result[:10]:
        description = '\n'.join(['%s: %s' % (title, item[title]) for title in titles])[:60]
        action_list = [PostbackAction(label='Book a meeting',
                                      data=item['Name'],
                                      text='Book a meeting with %s' % item['Name'])]
        obj = CarouselColumn(text=description,
                             title=item['Name'][:40],
                             actions=action_list)
        carousel_list.append(obj)

    carousel_template = CarouselTemplate(columns=carousel_list)
    template_message = TemplateSendMessage(
            alt_text='Here are the companies/resellers we found',
            template=carousel_template)
    return template_message

def check_for_keyword_search(intent):
    try:
        if intent['action'] == 'find_reseller.find_reseller-fallback':
            country = intent['outputContexts'][0]['parameters']['Country']
            keyword = intent['queryText'].replace(' ', '')
            result = search_reseller(keyword, country)
            if len(result) > 0:
                return True, make_carousel_object(result)
            else:
                return True, TextSendMessage(text="Sorry, we can't find any companies/resellers similar to [%s] in %s. Or you can try some other keywords?" % (keyword, country))
    except:
        return False, ''
