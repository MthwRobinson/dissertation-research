""" Utility for loading Meetup data into the database """
import datetime
import logging
from time import sleep

import arrow
import daiquiri
import pandas as pd

from pymeetup import Meetup
from research_utils import Database

class DataLoader:
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database()
        self.meetup = Meetup()

    def load_data(self):
        """ Loads data into the database. """
        self.load_groups()
        self.load_events()

    def load_groups(self):
        """ Loads groups into the database. """
        groups = self.get_groups()
        for group in groups:
            group_ = self.database.get_item('groups', group[0])
            if not group_:
                item = {'id': group[0],
                        'name': group[1],
                        'members': group[2],
                        'past_event_count': group[3]}
                self.database.delete_item('groups', group[0])
                self.database.load_item(item, 'groups')

    def get_groups(self):
        """ Pulls a list of groups to include in the data. """
        orders = ['most_active', 'newest', 'distance']
        all_groups = set()
        for order in orders:
            groups = self.meetup.find_groups(page=200, zip_code=20001,
                                            radius=25, order=order,
                                            fields=['past_event_count'])
            for group in groups:
                id_ = group['urlname']
                name = group['name']
                members = group['members']
                if 'past_event_count' in group:
                    past_event_count = group['past_event_count']
                else:
                    past_event_count = None
                entry = (id_, name, members, past_event_count)
                all_groups.add(entry)
        return all_groups

    def load_events(self):
        """ Loads events into the database. """
        sql = """
            SELECT *
            FROM dissertation.groups
            WHERE id NOT IN (SELECT DISTINCT group_id
                             FROM dissertation.events)
        """
        groups = pd.read_sql(sql, self.database.connection)
        for i in groups.index:
            group = dict(groups.loc[i])
            msg = 'Loading: {}'.format(group['name'])
            self.logger.info(msg)
            events = self.meetup.get_events(group['id'], page=1000,
                                            no_earlier_than='2009-01-01',
                                            no_later_than='2019-01-01')
            for event in events:
                timestamp = arrow.get(event['time']/1000).datetime
                item = {'id': event['id'], 'group_id': group['id'],
                        'name': event['name'], 'event_time': timestamp,
                        'yes_rsvp_count': event['yes_rsvp_count']}
                self.database.delete_item('events', event['id'])
                self.database.load_item(item, 'events')
                sleep(5)
            sleep(5)

    def load_attendees(self):
        """ Loads the attendees into the database. """
        forbidden = []
        sql = """
            SELECT *
            FROM dissertation.events
            WHERE id NOT IN (SELECT DISTINCT event_id
                             FROM dissertation.attendees)
        """
        events = pd.read_sql(sql, self.database.connection)
        for i in events.index:
            event = dict(events.loc[i])
            if event['group_id'] in forbidden:
                continue
            msg = 'Loading: {}-{}'.format(event['group_id'], event['id'])
            self.logger.info(msg)
            try:
                attendees = self.meetup.get_event_rsvps(event['group_id'], event['id'],
                                                        response='yes')
            except ValueError:
                msg = 'Adding {} to forbidden.'.format(event['group_id'])
                self.logger.warning(msg)
                forbidden.append(event['group_id'])
                continue

            for attendee in attendees:
                if attendee['response'] == 'yes':
                    sql = """
                        INSERT INTO dissertation.attendees
                        (member_id, event_id, group_id)
                        VALUES ('{}', '{}', '{}')
                    """.format(attendee['member']['id'], event['id'],
                               event['group_id'])
                    self.database.run_query(sql)
            sleep(5)
        sleep(5)
