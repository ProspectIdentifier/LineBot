import os
import logging
from decouple import config

# create logger
logger_i = logging.getLogger('Prospectidentifier')
logger_i.setLevel(logging.DEBUG)

logger_e = logging.getLogger('ProspectidentifierError')
logger_e.setLevel(logging.DEBUG)


# create file handler which logs even debug messages
if not os.path.exists(config('LOG_FOLDER')):
    os.makedirs(config('LOG_FOLDER'))

fh = logging.FileHandler(config('LOG_FOLDER') + 'Prospectidentifier.log')
fh.setLevel(logging.DEBUG)


# create console handler with a higher log level
ch = logging.FileHandler(config('LOG_FOLDER') + 'ERROR.log')
ch.setLevel(logging.ERROR)


# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)


# add the handlers to the logger
logger_i.addHandler(fh)
logger_e.addHandler(ch)


def infra_status(action, uuid):
    '''The infra layer'''
    logger_i.info('infra - %s - %s' %(action, uuid))

def application_status(action, uuid):
    '''The application layer'''
    logger_i.info('application - %s - %s' %(action, uuid))

def business_status(action, uuid):
    '''The business layer'''
    logger_i.info('business - %s - %s' %(action, uuid))

def error_status(err_msg, uuid):
	logger_e.error('%s - %s' %(uuid, err_msg))

#infra_status('user_access', '123')
#application_status('user_create', '123')
#business_status('meeting', '123')
