# -*- coding: utf-8 -*-

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import json, tv_controller_api
from alexa.skills.smarthome import AlexaResponse

def lambda_handler(request, context):
    # Dump the request for logging - check the CloudWatch logs
    print('lambda_handler request')
    print(json.dumps(request))

    if context is not None:
        print('lambda_handler context')
        print(context)

    # Validate we have an Alexa directive
    if 'directive' not in request:
        aer = AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'INVALID_DIRECTIVE',
                     'message': 'Missing key: directive, Is the request a valid Alexa Directive?'})
        return send_response(aer.get())

    # Check the payload version
    payload_version = request['directive']['header']['payloadVersion']
    if payload_version != '3':
        aer = AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'INTERNAL_ERROR',
                     'message': 'This skill only supports Smart Home API version 3'})
        return send_response(aer.get())

    # Crack open the request and see what is being requested
    name = request['directive']['header']['name']
    namespace = request['directive']['header']['namespace']

    # Handle the incoming request from Alexa based on the namespace

    if namespace == 'Alexa.Authorization':
        if name == 'AcceptGrant':
            # Note: This sample accepts any grant request
            # In your implementation you would use the code and token to get and store access tokens
            grant_code = request['directive']['payload']['grant']['code']
            grantee_token = request['directive']['payload']['grantee']['token']
            aar = AlexaResponse(namespace='Alexa.Authorization', name='AcceptGrant.Response')
            return send_response(aar.get())

    if namespace == 'Alexa.Discovery':
        if name == 'Discover':
            adr = AlexaResponse(namespace='Alexa.Discovery', name='Discover.Response')
            
            capability_alexa = adr.create_payload_endpoint_capability()
            
            capability_alexa_power_controller = adr.create_payload_endpoint_capability(
                interface='Alexa.PowerController',
                supported=[{'name': 'powerState'}])
            capability_alexa_stepSpeaker_controller = adr.create_payload_endpoint_capability(
                interface='Alexa.StepSpeaker')
            capability_alexa_playback_controller = adr.create_payload_endpoint_capability(
                interface='Alexa.PlaybackController',
                supportedOperations=['Play', 'Pause', 'Stop'])
                
            adr.add_payload_endpoint(
                friendly_name='TV',
                endpoint_id='ps3-tv',
                manufacturer_name='Sony',
                description='PlayStation 3 TV connected with Raspberry Pi',
                displayCategories=['TV'],
                capabilities=[capability_alexa, capability_alexa_power_controller, capability_alexa_stepSpeaker_controller, capability_alexa_playback_controller])
                
            return send_response(adr.get())

    if namespace == 'Alexa.PowerController':
        # Note: This sample always returns a success response for either a request to TurnOff or TurnOn
        endpoint_id = request['directive']['endpoint']['endpointId']
        power_state_value = 'OFF' if name == 'TurnOff' else 'ON'
        correlation_token = request['directive']['header']['correlationToken']
        
        try:
            tv_controller_api.tv_toggle(power_state_value)
        except Exception as error:
            print(error)
            
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}
            ).get()
                
        apcr = AlexaResponse(correlation_token=correlation_token)
        apcr.add_context_property(namespace='Alexa.PowerController', name='powerState', value=power_state_value)
    elif namespace == 'Alexa.StepSpeaker':
        endpoint_id = request['directive']['endpoint']['endpointId']
        correlation_token = request['directive']['header']['correlationToken']
        
        try:
            if name == 'AdjustVolume':
                response = tv_controller_api.tv_volume_step(request['directive']['payload']['volumeSteps'])
            else:
                return AlexaResponse(
                    name='ErrorResponse',
                    payload={'type': 'INTERNAL_ERROR','message': 'There was an error with the endpoint.'}
                ).get()
        except Exception as error:
            print(error)
            
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}
            ).get()
        
        apcr = AlexaResponse(correlation_token=correlation_token)
        apcr.add_context_property(namespace='Alexa.StepSpeaker', name='volumeSteps', value=request['directive']['payload']['volumeSteps'])
    elif namespace == 'Alexa.PlaybackController':
        endpoint_id = request['directive']['endpoint']['endpointId']
        correlation_token = request['directive']['header']['correlationToken']
        
        try:
            if name == 'Play' or name == 'Pause' or name == 'Stop':
                response = tv_controller_api.tv_playback_controller(name)
            else:
                return AlexaResponse(
                    name='ErrorResponse',
                    payload={'type': 'INTERNAL_ERROR','message': 'There was an error with the endpoint.'}
                ).get()
        except Exception as error:
            print(error)
            
            return AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint.'}
            ).get()
        
        apcr = AlexaResponse(correlation_token=correlation_token)
        apcr.add_context_property(namespace='Alexa.PlaybackController', name='action', value=name)
        
    return send_response(apcr.get())

def send_response(response):
    # TODO Validate the response
    print('lambda_handler response')
    print(json.dumps(response))
    return response