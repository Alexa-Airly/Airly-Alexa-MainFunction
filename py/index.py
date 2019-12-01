""" Main Function for Alexa Airly """

import json
import os
import requests
import boto3

import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractExceptionHandler,
    AbstractResponseInterceptor,
    AbstractRequestInterceptor)
from ask_sdk_core.utils import (
    is_request_type,
    is_intent_name)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.dialog import (
    ElicitSlotDirective, DelegateDirective)
from ask_sdk_model import (
    Response,
    IntentRequest,
    DialogState,
    SlotConfirmationStatus,
    Slot)
from ask_sdk_model.slu.entityresolution import StatusCode

""" Global parameters """
apikey = os.environ.get('APIKEY')
apiurlbase = os.environ.get('APIURLBASE')
maxdistance = os.environ.get('MAXDISTANCE')
maxresults = os.environ.get('MAXRESULTS')

pollutants = [
    {'name': 'PM10', 'type': 'PM10', 'symbol': '\u2B1B'},
    {'name': 'PM25', 'type': 'PM2.5', 'symbol': '\u25FE'},
    {'name': 'PM1', 'type': 'PM1.0', 'symbol': '\u25AA'},
]
index_levels = [
    {'name': 'VERY_LOW', 'symbol': '\U0001F600'},
    {'name': 'LOW', 'symbol': '\U0001F609'},
    {'name': 'MEDIUM', 'symbol': '\U0001F612'},
    {'name': 'HIGH', 'symbol': '\U0001F616'},
    {'name': 'VERY_HIGH', 'symbol': '\U0001F621'}
]

""" Temporary data """
locationlat = '50.062006'
locationlng = '19.940984'

sb = SkillBuilder()

def callAPI(apikey, params):
    headers = {
        'content-type': 'application/json',
        'apikey': apikey
    }

    apirequestlocation = 'nearest?lat={}&lng={}&maxDistanceKM={}&maxResults={}'.format(
        locationlat,
        locationlng,
        maxdistance,
        maxresults
    )

    apirequest = '{}/{}/{}'.format(
        apiurlbase,
        apirequesttype,
        apirequestlocation
    )

    response = requests.get(apirequest, headers=headers, params=None)

    return response.json()

def get_slot_values(filled_slots):
    """Return slot values with additional info."""
    slot_values = {}

    for key, slot_item in six.iteritems(filled_slots):
        name = slot_item.name
        try:
            status_code = slot_item.resolutions.resolutions_per_authority[0].status.code

            if status_code == StatusCode.ER_SUCCESS_MATCH:
                slot_values[name] = {
                    "synonym": slot_item.value,
                    "resolved": slot_item.resolutions.resolutions_per_authority[0].values[0].value.name,
                    "is_validated": True,
                }
            elif status_code == StatusCode.ER_SUCCESS_NO_MATCH:
                slot_values[name] = {
                    "synonym": slot_item.value,
                    "resolved": slot_item.value,
                    "is_validated": False,
                }
            else:
                pass
        except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
            logger.info("Couldn't resolve status_code for slot item: {}".format(slot_item))
            logger.info(e)
            slot_values[name] = {
                "synonym": slot_item.value,
                "resolved": slot_item.value,
                "is_validated": False,
            }
    return slot_values

""" Default classes """

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Hello, Cloud Control is waiting for your instructions."
        reprompt = "Please, select the service to manage."

        handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(
            SimpleCard("Cloud Control", speech_text)).set_should_end_session(
                False)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I'm Cloud Control. By using proper command you can \
            manage AWS EC2 resources."

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard(
                "Cloud Control", speech_text))
        return handler_input.response_builder.response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Cloud Control", speech_text))
        return handler_input.response_builder.response

class FallbackIntentHandler(AbstractRequestHandler):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "I cannot comply. "
            "Please, rephrase your statement.")
        reprompt = "does not compute!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Does not compute!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

class InProgressStatusIntentHandler(AbstractRequestHandler):
    """Get Airly Status in progress"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("status")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In InProgressStatusIntentHandler")
        current_intent = handler_input.request_envelope.request.intent
        prompt = ""

        for slot_name, current_slot in six.iteritems(current_intent.slots):
            if slot_name in ["EcInstanceSgSelector", "EcInstanceKeySelector",
                             "EcInstanceNameSelector", "EcInstanceTypeSelector",
                             "EcInstanceSubnetSelector"]:
                if (current_slot.confirmation_status != SlotConfirmationStatus.CONFIRMED
                        and current_slot.resolutions
                        and current_slot.resolutions.resolutions_per_authority[0]):
                    if current_slot.resolutions.resolutions_per_authority[0].status.code == StatusCode.ER_SUCCESS_MATCH:
                        if len(current_slot.resolutions.resolutions_per_authority[0].values) > 1:
                            prompt = "Select "

                            values = " or ".join([e.value.name for e in current_slot.resolutions.resolutions_per_authority[0].values])
                            prompt += values + " ?"
                            return handler_input.response_builder.speak(
                                prompt).ask(prompt).add_directive(
                                    ElicitSlotDirective(slot_to_elicit=current_slot.name)
                                    ).response
                    elif current_slot.resolutions.resolutions_per_authority[0].status.code == StatusCode.ER_SUCCESS_NO_MATCH:
                        if current_slot.name in required_slots:
                            prompt = "What {} are you looking for?".format(current_slot.name)

                            return handler_input.response_builder.speak(
                                prompt).ask(prompt).add_directive(
                                    ElicitSlotDirective(
                                        slot_to_elicit=current_slot.name
                                    )).response

        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=current_intent
            )).response

class CompletedStatusIntentHandler(AbstractRequestHandler):
    """Get Airly Status completed"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("status")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CompletedstatusIntentHandler")
        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = get_slot_values(filled_slots)

        try:
            # create list of values
            intent_payload = [
                slot_values["location"]["resolved"].replace(" ", "-")
            ]
            # log payload for ec2 create process
            #logger.info('\n'.join(map(str, ec2_instance_payload)))
            #success_code, msg = callAPI(apikey, intent_payload)
            #speech = msg
            speech = "Check your Cloudwatch"

        except Exception as e:
            speech = ("I am really sorry. I am unable to access part of my "
                      "memory. Please try again later")
            logger.info("Intent: {}: message: {}".format(
                handler_input.request_envelope.request.intent.name, str(e)))

        reprompt = "I am waiting for new instruction."
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            SimpleCard("Cloud Control", speech)).set_should_end_session(
                False)

        return handler_input.response_builder.speak(speech).response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(InProgressStatusIntentHandler())
sb.add_request_handler(CompletedStatusIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()

