from __future__ import print_function
from pywapi import get_countries_from_google,get_loc_id_from_weather_com,get_weather_from_weather_com,get_location_ids

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit Weather Report. " \
                    "Please tell me the country name as,country name is india "

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me the country name as,country name is india"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit Weather Report " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def country_name_attribute(country_name):
    print("with in validation fn:" , country_name)
    countries = get_countries_from_google('en')
    country_lst = []
    for ele in countries:
        country_lst.append(ele['name'])

    if country_name in country_lst:
        return {"country": country_name}
    else:
        return {"country": "Invalid"}
            

def city_name_attribute(city_name,session):
    lookup = get_location_ids(city_name)
    if not lookup:
        return {"city": "invalid"}
    else:
        return {"city": city_name}
    
def set_country_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    op = "country"
    if 'Countryname' in intent['slots']:
        country_name = intent['slots']['Countryname']['value']
        print("country name from intent:" , country_name)
        session_attributes = country_name_attribute(country_name)
        print("country in session:", session_attributes['country'])
        if country_name == session_attributes['country']:
            op = "You have given country name  " + \
                 country_name + \
                 ". Please tell me the city name by saying " \
                 " city name hyderabad "
        else:
            op = "You have entered invalid country name please retry by giving a valid country name "
    speech_output = op
    reprompt_text = op
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_city_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    status = False
    op = "Please Enter Country first"
    print("after getting city")
    if 'Cityname' in intent['slots']:
        city_name = intent['slots']['Cityname']['value']
        session_attributes = city_name_attribute(city_name,session)
        print(session_attributes['city'])
        if city_name == session_attributes['city']:
            if session.get('attributes', {}) and "country" in session.get('attributes', {}):
                country_name = session['attributes']['country']
                mystr = city_name +','+country_name
                lookup =get_loc_id_from_weather_com(mystr)
                if lookup['count'] == 0 :
                    print("city " + city_name + " Not in " + country_name)
                    op = "city name " + city_name + " not present in the given country  "
                    should_end_session = False
                else:
                    city_id = lookup[0][0]
                    weather_com_result = get_weather_from_weather_com(city_id)
                    op ="Weather of " + city_name + " in " + session['attributes']['country'] +" country - " + \
                    " day : " + weather_com_result['forecasts'][0]['day_of_week'] + " , "  + \
                    " sunrise : " + weather_com_result['forecasts'][0]['sunrise'] +  " , "  + \
                    " sunset : " + weather_com_result['forecasts'][0]['sunset'] +  "," + \
                    " max : " + weather_com_result['forecasts'][0]['high'] + "," + \
                    "min : " +  weather_com_result['forecasts'][0]['low'] + "," + \
                    "weather is : " + weather_com_result['current_conditions']['text'].lower() + \
                    " and " + weather_com_result['current_conditions']['temperature'] + " C. Good Bye "
                   
        else:
            op = "Invalid City name please retry by giving country and city names"
            status = False
    else:
        op = "City name not present in intent"
    speech_output = op
    reprompt_text = op
    should_end_session = status
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhatsMyWeatherIntent":
        return get_welcome_response()
    elif intent_name == "MyCountryIsIntent":
        return set_country_in_session(intent, session)
    elif intent_name == "MyCityIsIntent":
         return set_city_in_session(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
    if(should_end_session):
       handle_session_end_request()
    else:
        set_city_in_session(intent, session)

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
