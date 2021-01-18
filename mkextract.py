import os
import json
import subprocess

SUBTITLES_CODECS = {
    'S_KATE': 'ogg',
    'S_VOBSUB': 'sub',
    'S_TEXT/ASS': 'ass',
    'S_TEXT/SSA': 'ass',
    'S_TEXT/USF': 'usf',
    'S_HDMV/PGS': 'sup',
    'S_TEXT/UTF8': 'srt'
}

class MkExtract:
    def __init__(self, path):
        self.path = path
        self.basename = os.path.splitext(self.path)[0]
        self.attachments_folder = f'{self.basename}_Attachments'
        self.mkvmerge = 'mkvmerge'
        self.mkvextract = 'mkvextract'
        self.matroska = self.matroska_data()

    def matroska_data(self):
        command = [self.mkvmerge, '-i', '-F', 'JSON', self.path]
        return json.loads(subprocess.check_output(command, encoding='utf-8', universal_newlines=True))

    def get_attachments(self):
        if self.matroska['attachments'] != None:
            if not os.path.exists(self.attachments_folder):
                os.mkdir(self.attachments_folder)

        for attachment in self.matroska['attachments']:
            attachment_id = attachment['id']
            attachment_name = attachment['file_name']
            command = [self.mkvextract, self.path, 'attachments', f'{attachment_id}:{self.attachments_folder}/{attachment_name}']
            subprocess.call(command)

    def get_chapters(self):
        if self.matroska['chapters'] != None:
            command = [self.mkvextract, self.path, 'chapters', f'{self.basename}.xml']
            subprocess.call(command)

    def get_subtitles(self):
        for codec, extension in SUBTITLES_CODECS.items():
            for track in self.matroska['tracks']:
                if codec in track['properties']['codec_id']:
                    track_id = track['id']
                    track_number = track['properties']['number']
                    track_language = track['properties']['language']
                    command = [self.mkvextract, self.path, 'tracks', f'{track_id}:{self.basename}.{track_number}.{track_language}.{extension}']
                    subprocess.call(command)
