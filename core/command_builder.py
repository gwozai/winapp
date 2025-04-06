import os
from urllib.parse import unquote
from .models import CmdCommand

class CommandBuilder:
    archive_ext = {'.zip', '.rar', '.7z'}
    text_ext = {'.txt', '.md', '.json', '.log', '.csv'}

    def __init__(self, minio_client):
        self.minio_client = minio_client

    def build_for_object(self, obj):
        filename = os.path.basename(unquote(obj.object_name))
        ext = os.path.splitext(filename)[1].lower()
        url = self.minio_client.get_presigned_url(obj.object_name)

        if ext in self.archive_ext:
            foldername = os.path.splitext(filename)[0]
            cmd = f'mkdir "{foldername}" 2>nul && curl -o "{filename}" "{url}" && powershell -command "Expand-Archive -Path \"{filename}\" -DestinationPath .\{foldername} -Force" && del "{filename}"'
            return CmdCommand(filename, 'archive', cmd)
        elif ext in self.text_ext:
            cmd = f'powershell -Command "Set-Clipboard -Value (Invoke-WebRequest -Uri '{url}').Content"'
            return CmdCommand(filename, 'text', cmd)
        else:
            cmd = f'curl -O "{url}"'
            return CmdCommand(filename, 'other', cmd)