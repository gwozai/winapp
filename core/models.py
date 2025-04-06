class CmdCommand:
    def __init__(self, filename, cmd_type, command):
        self.filename = filename
        self.cmd_type = cmd_type
        self.command = command

    def __str__(self):
        type_label = {
            'archive': '📦 解压文件',
            'text': '📋 文本复制',
            'other': '📥 普通文件'
        }.get(self.cmd_type, '📁 其他')

        return f"{type_label} - {self.filename}：\n{self.command}"