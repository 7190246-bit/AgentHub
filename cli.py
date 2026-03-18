"""
AgentHub CLI - 命令行接口
"""

import sys
from typing import List

from agenthub import (
    AgentHub,
    registry,
    Command,
    READ, WRITE, META,
    start_daemon,
    stop_daemon,
    StateManager,
)


class AgentHubCLI:
    """AgentHub 命令行接口"""

    def __init__(self):
        self.hub = AgentHub()
        self.state_manager = StateManager()
        self.current_agent_id = None
        self.daemon = None

    def execute(self, command: str, args: List[str]):
        """执行命令"""
        # 去除斜杠前缀
        command = command.lstrip("/")

        cmd = registry.get_command(command)
        if not cmd:
            return {"error": f"未知命令: {command}. 运行 /help 查看帮助"}

        try:
            return cmd.handler(self.hub, args)
        except Exception as e:
            return {"error": f"执行失败: {str(e)}"}

    def run_interactive(self):
        """运行交互式命令行"""
        print("=" * 50)
        print("🚀 AgentHub 交互式命令行")
        print("=" * 50)
        print("输入 'help' 查看帮助，'exit' 或 'quit' 退出")
        print()

        while True:
            try:
                user_input = input("AgentHub> ").strip()

                if not user_input:
                    continue

                if user_input in ["exit", "quit"]:
                    print("👋 再见！")
                    break

                if user_input in ["help", "?"]:
                    print(registry.get_help())
                    continue

                # 解析命令和参数
                parts = user_input.split()
                command = parts[0]
                args = parts[1:]

                result = self.execute(command, args)

                if "error" in result:
                    print(f"❌ {result['error']}")
                elif "success" in result:
                    print("✅ 操作成功")
                    # 美化输出
                    for key, value in result.items():
                        if key != "success":
                            if isinstance(value, list):
                                print(f"  {key}: {len(value)} 项")
                            elif isinstance(value, dict):
                                print(f"  {key}:")
                                for k, v in value.items():
                                    print(f"    {k}: {v}")
                            else:
                                print(f"  {key}: {value}")
                else:
                    print(f"✅ {result}")

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except EOFError:
                print("\n\n👋 再见！")
                break


def main():
    """主函数 - 支持命令行和交互式"""
    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1]
        args = sys.argv[2:]

        cli = AgentHubCLI()

        # 守护进程特殊命令
        if command == "daemon":
            if args and args[0] == "start":
                print("启动 AgentHub 守护进程...")
                daemon = start_daemon(port=int(args[1]) if len(args) > 1 else None)
                print(f"守护进程已启动 (PID: {daemon.get_stats()['process_id']})")
                return 0
            elif args and args[0] == "stop":
                print("停止 AgentHub 守护进程...")
                stop_daemon()
                return 0

        # 普通命令
        result = cli.execute(command, args)

        if "error" in result:
            print(f"❌ {result['error']}")
            sys.exit(1)
        elif "success" in result:
            print("✅ 操作成功")
            # 美化输出
            for key, value in result.items():
                if key != "success":
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)} 项")
                    elif isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    else:
                        print(f"  {key}: {value}")
            sys.exit(0)
        else:
            print(f"✅ {result}")
            sys.exit(0)
    else:
        # 交互式模式
        cli = AgentHubCLI()
        cli.run_interactive()


if __name__ == "__main__":
    main()
