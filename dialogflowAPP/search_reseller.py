import requests
from decouple import config
import traceback
from dialogflowAPP.logrecoder import application_status#, error_status
from dialogflowAPP.models import ApplicationLog
from linebot.models import (CarouselTemplate, TemplateSendMessage,
                            CarouselColumn, TextSendMessage, URIAction)

# 'Address', 'Blocked', 'RecordType', 'Phone', 'Email', 'PostCode'
TITLES = ['NavisionID', 'City']
DATA = ['Address', 'Phone', 'Email', 'PostCode']

def search_reseller(keyword, country):
    '''search reseller's' information'''
    res = requests.get(config('RESELLER') % (country, keyword))
    res = res.json()
    return res['Results']

def make_carousel_object(result):
    '''Message Template'''
    carousel_list = []

    for item in result[:10]:
        description = '\n'.join(['%s: %s' % (title, item[title]) for title in TITLES])[:60]
        action_list = [
            URIAction(label='Company Summary',
                      uri='line://app/1611201899-GaVvEBB3?id='+item['NavisionID']),
            URIAction(label='Contact List',
                      uri='line://app/1611201899-xj78kWWZ?id='+item['NavisionID']),
            URIAction(label='Interesting',
                      uri='line://app/1611201899-mkn59qqz?id='+item['NavisionID']),
        ]
        obj = CarouselColumn(text=description,
                             title=item['Name'][:40],
                             actions=action_list)
        carousel_list.append(obj)

    carousel_template = CarouselTemplate(columns=carousel_list)
    template_message = TemplateSendMessage(
        alt_text='Here are the companies/resellers we found',
        template=carousel_template)
    return template_message

def check_for_keyword_search(intent, msg):
    '''the keyword of the company'''
    try:
        if intent['action'] == 'find_reseller.find_reseller-fallback':
            country = intent['outputContexts'][0]['parameters']['Country']
            keyword = intent['queryText'].replace(' ', '')
            result = search_reseller(keyword, country)
            application_status('reseller_search', country, keyword, len(result), msg.source.user_id)
            ApplicationLog.objects.create(lineuserid=msg.source.user_id,
                                          action='reseller_search',
                                          country=country,
                                          keyword=keyword,
                                          result_num=len(result))
            if len(result) > 0:
                return True, make_carousel_object(result)
            return True, TextSendMessage(text="Sorry, we can't find any \
                                               companies/resellers similar \
                                               to [%s] in %s. Or you can \
                                               try some other keywords?" % (keyword, country))
        return False, ''
    except:
        #error_status(traceback.format_exc(), 'test')
        return False, ''
