import datetime
import logging
import random
import time

import requests

BASE_URL = 'https://api-school.kinderlime.com/api/web/'
PAGE_SIZE = 30


class ProcareRepository:
    def __init__(self, email, password, from_date):
        self._email = email
        self._password = password
        self._from_date = from_date

        self._logger = logging.getLogger('procare-repository')
        self._session = requests.Session()

    def __enter__(self):
        self._auth()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()

    def _auth(self):
        response = self._session.post(f'{BASE_URL}auth', json={'email': self._email, 'password': self._password})
        try:
            self._session.headers.update({'authorization': f"Bearer {response.json()['user']['auth_token']}"})
        except KeyError:
            self._logger.error(f'failed to authenticate with Procare. error details:\n\n    {response.text}\n')
            raise ConnectionRefusedError

    def get_kids(self):
        response = self._session.get(f'{BASE_URL}parent/kids')
        return response.json()['kids']

    def _get_media_generator(self, url, error_message, media_entries_list_name, media_url_field_name, created_field_name):
        page = 0

        while True:
            self._logger.info(f'getting media list ({media_url_field_name}, page {page})')
            response = self._session.get(url.format(page))

            if not response.ok:
                self._logger.warning(f'{error_message}: {response.content}')
                return []

            media_entries = [entry for entry in response.json()[media_entries_list_name] if datetime.date.fromisoformat(entry[created_field_name].split('T')[0]) >= self._from_date]
            media = self._download_media(media_entries, media_url_field_name)
            yield media

            if len(media) < PAGE_SIZE:
                return

            page += 1

    def _download_media(self, media_entries, media_url_field_name):
        media = []

        for entry in media_entries:
            try:
                media_url = entry[media_url_field_name]
            except KeyError:
                media.append({'url': media_url, 'media': ''})
                continue

            self._logger.info(f'downloading media at url: {media_url}')
            # download URLs are pre-authorized, some of which come from S3. the session authorization interferes with these URLs
            response = requests.get(media_url)

            if response.ok:
                media.append({'url': media_url, 'media': response.content})
            else:
                self._logger.warning(f'error downloading media: {response.content}')
                media.append({'url': media_url, 'media': ''})

            # add a random delay between each media request
            time.sleep(random.randint(1, 3))

        return media

    def get_learning_activities_photos(self, kid_id):
        return self._get_media_generator(f'{BASE_URL}parent/daily_activities/?kid_id={kid_id}&filters[daily_activity][activity_type]=learning_activity&page={"{}"}',
                                         'error getting learning activity photo entries', 'daily_activities', 'photo_url', 'activity_time')

    def get_photos(self):
        return self._get_media_generator(f'{BASE_URL}parent/photos/?page={"{}"}', 'error getting photo entries', 'photos', 'main_url', 'created_at')

    def get_videos(self):
        return self._get_media_generator(f'{BASE_URL}parent/videos/?page={"{}"}', 'error getting video entries', 'videos', 'video_file_url', 'created_at')