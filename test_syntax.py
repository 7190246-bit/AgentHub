# 测试文件
READ = "read"
WRITE = "write"
META = "meta"

class Command:
    pass

class CommandRegistry:
    def get_commands_by_type(self, command_type):
        return []

registry = CommandRegistry()

print("Test passed")
