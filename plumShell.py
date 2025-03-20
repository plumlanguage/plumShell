import sys
import os
import msvcrt
from ctypes import windll, byref, Structure, c_short, c_ushort, c_ulong
from pathlib import Path

class COORD(Structure):
    _fields_ = [("X", c_short), ("Y", c_short)]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", c_ushort),
        ("srWindow", c_short * 4),
        ("dwMaximumWindowSize", COORD),
    ]

ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
kernel32 = windll.kernel32
hStdOut = kernel32.GetStdHandle(-11)
original_mode = c_ulong()
kernel32.GetConsoleMode(hStdOut, byref(original_mode))
kernel32.SetConsoleMode(hStdOut, original_mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

def get_cursor_pos():
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(hStdOut, byref(csbi))
    return (csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y)

def set_cursor_pos(x, y):
    coord = COORD(x, y)
    kernel32.SetConsoleCursorPosition(hStdOut, coord)

# 关键修复：计算可见提示符长度（去除ANSI转义码）
PROMPT = "\033[32m> \033[0m"
VISIBLE_PROMPT_LEN = len("> ")  # 实际可见部分长度

COMMANDS = ['.exit', 'ver', '腐竹的腹肌香香的']

def get_completion(buffer):
    matches = [cmd for cmd in COMMANDS if cmd.startswith(buffer)]
    return os.path.commonprefix(matches)[len(buffer):] if matches else ''

def win_input():
    buffer = ''
    suggestion = ''
    
    # 初始绘制提示符（仅在此处绘制）
    sys.stdout.write(PROMPT)
    sys.stdout.flush()
    start_x, start_y = get_cursor_pos()
    start_x -= VISIBLE_PROMPT_LEN  # 关键修正
    
    while True:
        suggestion = get_completion(buffer)
        display_text = buffer + suggestion
        
        # 清除并重绘当前行
        set_cursor_pos(start_x, start_y)
        sys.stdout.write('\033[K')  # 清除整行
        sys.stdout.write(PROMPT + display_text)
        sys.stdout.flush()
        
        # 计算光标位置（GBK编码处理中文）
        current_len = len(buffer.encode('gbk'))
        set_cursor_pos(start_x + VISIBLE_PROMPT_LEN + current_len, start_y)
        
        ch = msvcrt.getwch()
        
        if ch == '\r':
            sys.stdout.write('\n')
            return buffer + suggestion
        elif ch == '\t' and suggestion:
            buffer += suggestion
        elif ch == '\x08':
            if buffer:
                buffer = buffer[:-1]
        elif ch == '\xe0':
            msvcrt.getwch()
        elif ord(ch) < 32:
            continue
        else:
            buffer += ch

if __name__ == '__main__':
    os.system('cls')
    kernel32.SetConsoleTitleW("plumShell B-001")
    appdata_path = os.getenv('APPDATA')
    print(f"Get Start File: {Path(appdata_path).joinpath('plumShellData/startFile.txt')}")
    print(open(Path(appdata_path).joinpath('plumShellData/startFile.txt'), 'r', encoding='utf-8').read())
    work_path = os.getcwd()
    # 从文件加载额外命令
    COMMANDS_FILE = Path(appdata_path).joinpath('plumShellData/commands.txt')
    try:
        with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
            # 逐行读取并去除换行符
            COMMANDS += [line.rstrip('\n') for line in f if line.strip()]  # 跳过空行
    except FileNotFoundError:
        print(f"\033[33m[提示] 未找到命令文件 {COMMANDS_FILE}，仅使用内置命令\033[0m")
    except Exception as e:
        print(f"\033[31m[错误] 读取命令文件失败: {str(e)}\033[0m")
        
    try:
        while True:
            print("")
            print(f"[\033[32m{work_path}\033[0m]")
            user_input = win_input()  # 该函数内部已包含提示符绘制
            # print(f"\033[33m输入内容: {user_input}\033[0m\n")
            x = user_input.split(" ")
            if x[0] == '.exit':
                exit(0)
            elif x[0] == "腐竹的腹肌香香的":
                print("腐竹的腹肌香香的，鸡巴软软的，声音奶奶的，rua一口~")      
            elif x[0] == "ver":
                print("plumShell B-001")
            else:
                # 检查命令是否存在
                comFile = Path(appdata_path).joinpath(f'plumShellData/com/{x[0]}/{x[1]}.exe')
                # 尝试执行命令
                if comFile.exists():
                    # 修改为直接执行命令，不在新窗口中启动
                    os.system(str(comFile))
                else:
                    print(f"命令 '{x[0]}' 未找到。")
        
    finally:
        kernel32.SetConsoleMode(hStdOut, original_mode.value)