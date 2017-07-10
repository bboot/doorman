# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Carry out voice commands by recognising keywords."""

import actionbase
import datetime
import entity
import logging
import random
import re
import subprocess
from twilio.rest import Client
import yaml


# =============================================================================
#
# Hey, Makers!
#
# This file contains some examples of voice commands that are handled locally,
# right on your Raspberry Pi.
#
# Do you want to add a new voice command? Check out the instructions at:
# https://aiyprojects.withgoogle.com/voice/#makers-guide-3-3--create-a-new-voice-command-or-action
# (MagPi readers - watch out! You should switch to the instructions in the link
#  above, since there's a mistake in the MagPi instructions.)
#
# In order to make a new voice command, you need to do two things. First, make a
# new action where it says:
#   "Implement your own actions here"
# Secondly, add your new voice command to the actor near the bottom of the file,
# where it says:
#   "Add your own voice commands here"
#
# =============================================================================

# Actions might not use the user's command. pylint: disable=unused-argument


# Example: Say a simple response
# ================================
#
# This example will respond to the user by saying something. You choose what it
# says when you add the command below - look for SpeakAction at the bottom of
# the file.
#
# There are two functions:
# __init__ is called when the voice commands are configured, and stores
# information about how the action should work:
#   - self.say is a function that says some text aloud.
#   - self.words are the words to use as the response.
# run is called when the voice command is used. It gets the user's exact voice
# command as a parameter.

class SpeakAction(object):

    """Says the given text via TTS."""

    def __init__(self, say, words):
        self.say = say
        self.words = words

    def run(self, voice_command):
        self.say(self.words)


# Example: Tell the current time
# ==============================
#
# This example will tell the time aloud. The to_str function will turn the time
# into helpful text (for example, "It is twenty past four."). The run function
# uses to_str say it aloud.

class SpeakTime(object):

    """Says the current local time with TTS."""

    def __init__(self, say):
        self.say = say

    def run(self, voice_command):
        time_str = self.to_str(datetime.datetime.now())
        self.say(time_str)

    def to_str(self, dt):
        """Convert a datetime to a human-readable string."""
        HRS_TEXT = ['midnight', 'one', 'two', 'three', 'four', 'five', 'six',
                    'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
        MINS_TEXT = ["five", "ten", "quarter", "twenty", "twenty-five", "half"]
        hour = dt.hour
        minute = dt.minute

        # convert to units of five minutes to the nearest hour
        minute_rounded = (minute + 2) // 5
        minute_is_inverted = minute_rounded > 6
        if minute_is_inverted:
            minute_rounded = 12 - minute_rounded
            hour = (hour + 1) % 24

        # convert time from 24-hour to 12-hour
        if hour > 12:
            hour -= 12

        if minute_rounded == 0:
            if hour == 0:
                return 'It is midnight.'
            return "It is %s o'clock." % HRS_TEXT[hour]

        if minute_is_inverted:
            return 'It is %s to %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])
        return 'It is %s past %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])


# Example: Run a shell command and say its output
# ===============================================
#
# This example will use a shell command to work out what to say. You choose the
# shell command when you add the voice command below - look for the example
# below where it says the IP address of the Raspberry Pi.

class SpeakShellCommandOutput(object):

    """Speaks out the output of a shell command."""

    def __init__(self, say, shell_command, failure_text):
        self.say = say
        self.shell_command = shell_command
        self.failure_text = failure_text

    def run(self, voice_command):
        output = subprocess.check_output(self.shell_command, shell=True).strip()
        if output:
            self.say(output)
        elif self.failure_text:
            self.say(self.failure_text)


# Example: Change the volume
# ==========================
#
# This example will can change the speaker volume of the Raspberry Pi. It uses
# the shell command SET_VOLUME to change the volume, and then GET_VOLUME gets
# the new volume. The example says the new volume aloud after changing the
# volume.

class VolumeControl(object):

    """Changes the volume and says the new level."""

    GET_VOLUME = r'amixer get Master | grep "Front Left:" | sed "s/.*\[\([0-9]\+\)%\].*/\1/"'
    SET_VOLUME = 'amixer -q set Master %d%%'

    def __init__(self, say, change):
        self.say = say
        self.change = change

    def run(self, voice_command):
        res = subprocess.check_output(VolumeControl.GET_VOLUME, shell=True).strip()
        try:
            logging.info("volume: %s", res)
            vol = int(res) + self.change
            vol = max(0, min(100, vol))
            subprocess.call(VolumeControl.SET_VOLUME % vol, shell=True)
            self.say(_('Volume at %d %%.') % vol)
        except (ValueError, subprocess.CalledProcessError):
            self.say(_('Sorry, I couldn\'t do that'))
            logging.exception("Error using amixer to adjust volume.")


# Example: Repeat after me
# ========================
#
# This example will repeat what the user said. It shows how you can access what
# the user said, and change what you do or how you respond.

class RepeatAfterMe(object):

    """Repeats the user's command."""

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword

    def run(self, voice_command):
        # The command still has the 'repeat after me' keyword, so we need to
        # remove it before saying whatever is left.
        to_repeat = voice_command.replace(self.keyword, '', 1)
        self.say(to_repeat)


# =========================================
# Makers! Implement your own actions here.
# =========================================


def make_actor(say):
    """Create an actor to carry out the user's commands."""

    entities = entity.Entities('/home/pi/entities2.yml')
    actor = actionbase.Actor()

    if False:
        actor.add_keyword(
            _('ip address'), SpeakShellCommandOutput(
                say, "ip -4 route get 1 | head -1 | cut -d' ' -f8",
                _('I do not have an ip address assigned to me.')))

        actor.add_keyword(_('volume up'), VolumeControl(say, 10))
        actor.add_keyword(_('volume down'), VolumeControl(say, -10))
        actor.add_keyword(_('max volume'), VolumeControl(say, 100))

        actor.add_keyword(_('repeat after me'),
                          RepeatAfterMe(say, _('repeat after me')))

    # =========================================
    # Makers! Add your own voice commands here.
    # =========================================
    for item in entities.units.values():
        unit = entity.Unit(item)
        logging.debug(unit)
        actor.add_keyword(unit.synonyms, PageUnit(say, unit))
    for item in entities.tenants.values():
        tenant = entity.Tenant(item)
        logging.debug(tenant)
        actor.add_keyword(tenant.synonyms, PageTenant(say, tenant))
    actor.add_keyword(GainEntry.synonyms, GainEntry(say, entities.tenants))
    actor.add_keyword(RequestPassword.synonyms,
                      RequestPassword(say, entities.tenants))
    return actor

class Messenger:
    with open('/home/pi/twilio.yml') as f:
        config = yaml.load(f)
    account_sid = config['account_sid']
    auth_token = config['auth_token']
    from_ = config['from']

    def __init__(self):
        self.client = Client(self.account_sid, self.auth_token)

    def send_text(self, to, msg):
        message = self.client.messages.create(to=to,
                                              from_=self.from_,
                                              body=msg)
        logging.debug(message.sid)


class Intent:
    ''' may contain a context.  context will be,
        for example, RequestPassword intent '''
    def __init__(self, context=None):
        self.context = context

class RequestPassword(Intent):
    synonyms = [
        "password",
        'forgot', # TODO: these are too general
        'help',
    ]
    responses = [
        "ok, $tenant, i've sent you a new password",
        "ok, $tenant, check your messages",
        "you got it, $tenant, i just texted you a new one.",
    ]
    token = '$tenant'
    def __init__(self, say, tenants, context=None):
        super().__init__(context)
        self.say = say
        # TODO: Need to query which tenant this is.  use context
        self.tenant = entity.Tenant(tenants['Bryan'])

    def run(self, voice_command):
        Password(self.tenant).new_word()
        response = random.choice(self.responses)
        response = response.replace(self.token,
                                    self.tenant.name)
        self.say(response)


WORDS_FILE="/home/pi/CROSSWD.TXT"
class Password:
    ''' this is an action class '''
    messenger = Messenger()
    with open(WORDS_FILE, "r") as f:
        words = f.readlines()

    def __init__(self, tenant):
        self.tenant = tenant

    def new_word(self):
        ''' 1. generate and persist new tenant-specific password
            2. send new password to tenant '''
        self.tenant.password = random.choice(self.words).rstrip()
        # logger.debug(self.tenant.word)
        # TODO: persist it
        self.messenger.send_text(self.tenant.phone_no,
                                 self.tenant.password)
        return self.tenant.password


class GainEntry(Intent):
    query_responses = [
        'hello, $tenant, please state the password',
        'good day, $tenant, what is your password?',
        'howdy, $tenant!  your password, please',
    ]
    pass_responses = [
        'hello, $tenant, have a wonderful day',
        'good day, $tenant, nice to see you',
        'howdy, $tenant!  another lovely day in the city',
    ]
    fail_responses = [
        'sorry, i could not let you in',
        'authorization has been denied.  please try again',
        "please check your password, it didn't match",
        "try spelling it out slowly next time",
    ]
    synonyms = [
        'let me in',
        'open up',
        'open the door',
        'knock knock',
    ]
    token = '$tenant'
    def __init__(self, say, tenants):
        self.say = say
        # TODO: Get which tenant it is based on the password used
        self.tenant = entity.Tenant(tenants['Bryan'])

    def run(self, voice_command):
        passed = False
        # TODO:
        # 1. listen for the password
        # 2. match the result to self.tenant.password
        # 3. on a match, give a greeting and buzz the door
        # TODO TEST CODE
        if self.tenant.password in voice_command.lower():
            response = 'that is the correct password: %s. '%(
                       self.tenant.password)
            response += random.choice(self.pass_responses)
            passed = True
        else:
            response = "i didn't recognize the password. "
            response += random.choice(self.fail_responses)
        response = response.replace(self.token, self.tenant.name)
        self.say(response)
        if passed:
            # do this at the end to reduce delay
            Password(self.tenant).new_word()
        # TODO TEST CODE
        return 1

class PageUnit(Intent):
    entity = '$unit'
    responses = [
        'please wait. paging unit $unit',
        'ok. paging unit $unit',
        'hang on while i page unit $unit',
        'you got it. paging unit $unit',
    ]
    def __init__(self, say, unit):
        self.unit = unit
        self.say = say
        if unit.paging_exception:
            self.responses = unit.paging_exception.message

    def say_unit(self, unit):
        ''' Pronounce unit number more like English
            E.g.: pronounce '453' as 'four fifty three' instead of
            'four hundred fifty three'
        '''
        try:
            val = int(re.findall(r'\d+', unit)[0])
            suf = ''
            match = re.match(r"([0-9]+)([a-z]+)", unit, re.I)
            if match:
                n, suf = match.groups()
            hun = int(val / 100)
            rem = int(val - (hun * 100))
            ret = '%s %s %s'%(hun, rem, suf)
        except Exception as e:
            return unit
        return ret

    def run(self, voice_command):
        response = random.choice(self.responses)
        response = response.replace(self.entity,
                                    self.say_unit(self.unit.address))
        self.say(response)
        if self.unit.paging_exception:
            return self.unit.paging_exception.run()
        # TODO: page the unit!
        return 1


class PageTenant(Intent):
    ''' in api.ai, the entity is @tenant.  The entity value is $tenant
        not sure what the distinction is for '''
    entity = '$tenant'
    responses = [
        'ok, paging $tenant',
        'ok, please stand by while i page $tenant',
        'sure, please wait while i page $tenant',
        'paging $tenant, please stand by',
        'ok, hang on while i page $tenant',
    ]
    def __init__(self, say, tenant):
        self.say = say
        self.tenant = tenant
        if tenant.paging_exception:
            self.responses = tenant.paging_exception.message

    def run(self, voice_command):
        response = random.choice(self.responses)
        self.say(response.replace(self.entity, self.tenant.name))
        if self.tenant.paging_exception:
            return self.tenant.paging_exception.run()
        # TODO: page the tenant!
        return 1


def add_commands_just_for_cloud_speech_api(actor, say):
    """Add simple commands that are only used with the Cloud Speech API."""
    def simple_command(keyword, response):
        actor.add_keyword(keyword, SpeakAction(say, response))

    simple_command('alexa', _("We've been friends since we were both starter projects"))
    simple_command(
        'beatbox',
        'pv zk pv pv zk pv zk kz zk pv pv pv zk pv zk zk pzk pzk pvzkpkzvpvzk kkkkkk bsch')
    simple_command(_('clap'), _('clap clap'))
    simple_command('google home', _('She taught me everything I know.'))
    simple_command(_('hello'), _('hello to you too'))
    simple_command(_('tell me a joke'),
                   _('What do you call an alligator in a vest? An investigator.'))
    simple_command(_('three laws of robotics'),
                   _("""The laws of robotics are
0: A robot may not injure a human being or, through inaction, allow a human
being to come to harm.
1: A robot must obey orders given it by human beings except where such orders
would conflict with the First Law.
2: A robot must protect its own existence as long as such protection does not
conflict with the First or Second Law."""))
    simple_command(_('where are you from'), _("A galaxy far, far, just kidding. I'm from Seattle."))
    simple_command(_('your name'), _('A machine has no name'))

    actor.add_keyword(_('time'), SpeakTime(say))
