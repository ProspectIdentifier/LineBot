import os
import logging
from decouple import config

# create logger
logger = logging.getLogger('Prospectidentifier')
logger.setLevel(logging.DEBUG)


# create file handler which logs even debug messages
if not os.path.exists(config('LOG_FOLDER')):
    os.makedirs(config('LOG_FOLDER'))

fh = logging.FileHandler(config('LOG_FOLDER') + 'Prospectidentifier.log')
fh.setLevel(logging.DEBUG)


# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)


# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)


# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def infra_status(action, uuid):
    '''The infra layer'''
    logger.info('infra - %s - %s' %(action, uuid))

def application_status(action, uuid):
    '''The application layer'''
    logger.info('application - %s - %s' %(action, uuid))

def business_status(action, uuid):
    '''The business layer'''
    logger.info('business - %s - %s' %(action, uuid))



#infra_status('user_access', '123')
#application_status('user_create', '123')
#business_status('meeting', '123')
