import argparse
import datetime
import io
import pathlib

import piexif

LATITUDE = ((39, 1), (58, 1), (431, 100))
LATITUDE_REF = b'N'
LONGITUDE = ((86, 1), (8, 1), (4346, 100))
LONGITUDE_REF = b'W'

def _parse_args():
    parser = argparse.ArgumentParser(description='renames and assigns EXIF attributes to downloaded Procare photos and videos')
    parser.add_argument('--input-dir', '-i', type=pathlib.Path, required=True, help='a directory containing downloaded Procare photos and videos')
    parser.add_argument('--output-dir', '-o', type=pathlib.Path, required=True, help='a directory for the resulting files')

    return parser.parse_args()

def cleanup_photos(input_dir_path, output_dir_path):
    for path in list(input_dir_path.glob('*.jpg')):
        file_bytes = path.read_bytes()
        exif_dict = piexif.load(file_bytes)

        exif_dict['0th'][piexif.ImageIFD.Software] = u'Procare'

        file_datetime = datetime.datetime.fromtimestamp(int(path.stem[:10]))
        file_datetime_exif = file_datetime.strftime("%Y:%m:%d %H:%M:%S") 
        exif_dict['0th'][piexif.ImageIFD.DateTime] = file_datetime_exif
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = file_datetime_exif
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = file_datetime_exif

        exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = LATITUDE
        exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = LATITUDE_REF
        exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = LONGITUDE
        exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = LONGITUDE_REF

        output_bytes = io.BytesIO()
        piexif.insert(piexif.dump(exif_dict), file_bytes, output_bytes)

        (output_dir_path / file_datetime.strftime('%Y%m%d_%H%M%S.jpg')).write_bytes(output_bytes.getbuffer())

def cleanup_videos(input_dir_path, output_dir_path):
    for path in input_dir_path.glob('*.mp4'):
        file_datetime = datetime.datetime.fromtimestamp(int(path.stem[:10]))
        path.rename((output_dir_path / file_datetime.strftime('%Y%m%d_%H%M%S.mp4')))

def main():
    args = _parse_args()

    input_dir_path = args.input_dir.expanduser()
    output_dir_path = args.output_dir.expanduser()

    cleanup_photos(input_dir_path, output_dir_path)
    cleanup_videos(input_dir_path, output_dir_path)

if __name__ == '__main__':
    main()