# -*- coding: utf-8 -*-

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core import attributes_manager
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, request_envelope
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Slot, SlotConfirmationStatus, DialogState
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model.dialog import DelegateDirective, ElicitSlotDirective

# Async Modules
import asyncio
import aiohttp

import logging
import re
import six
import requests


sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		return is_request_type("LaunchRequest")(handler_input)
	
	def handle(self, handler_input):
		attr = handler_input.attributes_manager.session_attributes
		if not attr:
			attr['fact'] = ''
		
		handler_input.attributes_manager.session_attributes = attr

		outputSpeech = "Welcome to Get Numbers or Dates fact. Would like to know a fact of today?"
		rePrompt = "Would you like to hear a fact from today?. Say, help for more information"

		handler_input.response_builder.speak(outputSpeech).set_card(SimpleCard("Get Facts", outputSpeech)).ask(rePrompt).set_should_end_session(False)
		return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		return is_intent_name("AMAZON.HelpIntent")(handler_input)
		
	def handle(self, handler_input):
		outputSpeech = "You can say: give me a fact from today or give me a fact of ten"
		handler_input.response_builder.speak(outputSpeech).ask(outputSpeech).set_card(SimpleCard("Get Numbers", outputSpeech))
		return handler_input.response_builder.response

class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        outputSpeech = "Thanks. Bye."

        handler_input.response_builder.speak(outputSpeech).set_card(SimpleCard("Get Numbers", outputSpeech))
        return handler_input.response_builder.set_should_end_session(True).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class AllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        # Log the exception in CloudWatch
        print(exception)

        outputSpeech = "Sorry, I think I did not get it. Say, help to get more information"
        handler_input.response_builder.speak(outputSpeech).set_card(SimpleCard("Get Numbers", outputSpeech)).ask(outputSpeech)
        return handler_input.response_builder.response

class GetNumberFactIntentHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		logger.info("In GetNumberFactIntentHandler")
		return is_intent_name("GetNumberFactIntent")(handler_input)
	
	def handle(self, handler_input):

		loop = asyncio.get_event_loop()
		outputSpeech, rePrompt = loop.run_until_complete(getNumberFact(handler_input))

		return handler_input.response_builder.speak(outputSpeech).set_card(SimpleCard("Get Numbers", outputSpeech)).ask(rePrompt).response

class GetDateFactIntentHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		logger.info("In GetDateFactIntentHandler")
		return is_intent_name("GetDateFactIntent")(handler_input)
	
	def handle(self, handler_input):

		loop = asyncio.get_event_loop()
		outputSpeech, rePrompt = loop.run_until_complete(getDateFact(handler_input))

		return handler_input.response_builder.speak(outputSpeech).set_card(SimpleCard("Get Numbers", outputSpeech)).ask(rePrompt).response

def saveSessionAttr(handler_input, attr):
	session_attr = handler_input.attributes_manager.session_attributes
	session_attr['evangelio'] = attr

	handler_input.attributes_manager.session_attributes = session_attr

async def getNumberFact(handler_input):
	currentIntent = handler_input.request_envelope.request.intent 
	basuURL = 'http://numbersapi.com/'
	headersDict = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
	}

	for slotName, currentSlot in six.iteritems(currentIntent.slots):
		if slotName == 'number':
			number = currentSlot.value

	url = f'{basuURL}{number}'

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headersDict) as resp:
			data = await resp.text()
	outputSpeech = data
	rePrompt = "Nothing"

	return (outputSpeech, rePrompt)

async def getDateFact(handler_input):
	currentIntent = handler_input.request_envelope.request.intent 
	basuURL = 'http://numbersapi.com/'
	headersDict = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
	}

	for slotName, currentSlot in six.iteritems(currentIntent.slots):
		if slotName == 'date':
			date = currentSlot.value
			
	date = '/'.join(date.split('-')[1:3])+ '/date'
	url = f'{basuURL}{date}'

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headersDict) as resp:
			data = await resp.text()
	outputSpeech = data
	rePrompt = "Nothing"

	return (outputSpeech, rePrompt)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetNumberFactIntentHandler())
sb.add_request_handler(GetDateFactIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()