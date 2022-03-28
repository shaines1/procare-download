import argparse
import datetime
import getpass
import logging
import pathlib
import re
import sys
import uuid

import _procare_repository

PHOTO_RE = '.*/img_([0-9]+).*'
VIDEO_RE = '.*\?([0-9]+)'

EPOCH = datetime.date(1970, 1, 1)

def _parse_args():
    def _parse_valid_date(s):
      try:
          return datetime.datetime.strptime(s, '%Y%m%d').date()
      except ValueError:
          raise argparse.ArgumentTypeError('date must be in format YYYYMMDD')

    parser = argparse.ArgumentParser(description='downloads photos and videos from Procare')
    parser.add_argument('--email', '-e', type=str, required=True, help='an email login')
    parser.add_argument('--download-path', '-d', type=pathlib.Path, required=True, help='a download path for the resulting files')
    parser.add_argument('--from-date', '-f', type=_parse_valid_date, help='a left inclusive date boundary')

    return parser.parse_args()

def _save_media(timestamp_regular_expression, file_extension, download_path, url, media):
    if not media:
      return

    try:
      timestamp = re.match(timestamp_regular_expression, url)[1]
    except Exception:
      logging.error(f'failed to parse timestamp for url: {url}')
      return

    file_path = (download_path / file_extension.format(timestamp))
    if file_path.exists():
      file_path = (download_path / file_extension.format(f'{timestamp}_{uuid.uuid4().hex}'))

    file_path.write_bytes(media)

def main():
    args = _parse_args()
    password = getpass.getpass()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    download_path = pathlib.Path(args.download_path).expanduser()
    download_path.mkdir(exist_ok=True)

    from_date = args.from_date or EPOCH

    with _procare_repository.ProcareRepository(args.email, password, from_date) as repository:
        for kid_id in {kid['id'] for kid in repository.get_kids()}:
            for photos in repository.get_learning_activities_photos(kid_id):
                for photo in photos:
                    _save_media(PHOTO_RE, '{}.jpg', download_path, photo['url'], photo['media'])

        for photos in repository.get_photos():
            for photo in photos:
                _save_media(PHOTO_RE, '{}.jpg', download_path, photo['url'], photo['media'])

        for videos in repository.get_videos():
            for video in videos:
                _save_media(VIDEO_RE, '{}.mp4', download_path, video['url'], video['media'])

if __name__ == '__main__':
    main()