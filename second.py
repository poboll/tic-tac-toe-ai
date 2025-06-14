#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三子棋AI系统 - 第二玩家(AI先手)主程序

本模块是三子棋AI系统的第二玩家主程序，AI作为先手玩家。
主要功能：
- AI先手，人类后手的游戏模式
- 通过计算机视觉检测人类玩家的棋子放置
- 使用Minimax算法计算AI的最佳移动
- 通过串口通信控制机械臂执行AI移动
- 实时检测游戏胜负和平局状态

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

游戏流程：
1. 用户输入AI的第一步移动位置(0-8)
2. AI执行第一步移动并发送指令给机械臂
3. 等待检测人类玩家的移动
4. AI计算并执行最佳反击移动
5. 重复步骤3-4直到游戏结束

通信协议：
- AI移动指令格式: '2' + 移动次数 + 目标位置
- 位置编号: 0-8 (3x3棋盘从左上到右下)

依赖模块：
- decision: 游戏逻辑和AI算法
- versionsecond: 计算机视觉检测(检测黑棋)
- communication: 串口通信
"""

from decision import init_board, print_board, computermove, winnerdetect, full, humanmove
from versionsecond import capture_and_process_image
import io
import sys
from communication import send_message

def main():
    """
    第二玩家主函数 - AI先手模式
    
    游戏控制流程：
    1. 初始化棋盘和检测位置集合
    2. 获取用户输入的AI第一步移动
    3. 进入主游戏循环：
       - 检测人类移动
       - 验证移动合法性
       - 检查游戏结束条件
       - 计算AI最佳移动
       - 发送移动指令给机械臂
       - 检查游戏结束条件
    
    异常处理：
    - 捕获串口通信异常
    - 处理计算机视觉检测失败
    - 处理AI算法计算异常
    """
    print("=== 三子棋AI系统 - 第二玩家模式(AI先手) ===")
    print("游戏规则：AI使用白棋(标记为2)，人类使用黑棋(标记为1)")
    print("AI将先手，请准备开始游戏...\n")
    # 初始化游戏状态
    chess = init_board()                    # 创建空的3x3棋盘
    detected_positions = set()              # 存储已检测到的棋子位置，防止重复检测
    print("初始棋盘状态:")
    print_board(chess)                      # 显示初始棋盘

    # 获取AI的第一步移动
    first_move = int(input("请输入AI第一步移动位置(0-8): "))
    
    # 验证输入的有效性
    if not (0 <= first_move <= 8):
        print("错误：位置必须在0-8之间")
        return
    
    # 执行AI的第一步移动
    print(f"\nAI执行第一步移动到位置 {first_move}")
    computermove(chess, first_move)         # AI在指定位置放置棋子
    computer_move_count = 1                 # AI移动计数器
    print(f"发送AI第一步指令: 11{first_move}")  # 第一步使用特殊指令格式
    print("\nAI第一步移动后的棋盘:")
    print_board(chess)                      # 显示更新后的棋盘
    
    print("\n等待人类玩家移动...")
    print("请在棋盘上放置黑棋，程序将自动检测")

    # 主游戏循环
    while True:
        # 标志位：跟踪棋盘是否发生变化
        position_changed = True
        
        # 使用计算机视觉检测人类玩家的移动
        print("\n正在检测人类玩家移动...")
        move = capture_and_process_image(detected_positions)
        
        if move is not None:
            # 检测到人类移动，验证并更新棋盘
            print(f"检测到人类在位置 {move[0]} 放置了棋子")
            chess, position_changed = humanmove(chess, move[0], detected_positions)
            print("\n人类移动后的棋盘:")
            print_board(chess)
            
            # 检查人类是否获胜
            if winnerdetect(chess, 1):
                print("\n🎉 人类玩家获胜！")
                print("游戏结束")
                break
            
            # 检查是否平局
            if full(chess):
                print("\n⚖️ 平局！")
                print("游戏结束")
                break
        else:
            print("未检测到有效移动，请重新放置棋子")
            continue

        # 如果棋盘状态发生了变化，AI计算并执行反击
        if not position_changed:
            print("\n轮到AI移动...")
            computer_move_count += 1
            
            # 捕获AI算法的输出(移动位置)
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            # 使用Minimax算法计算AI的最佳移动
            chess = computermove(chess)

            # 恢复标准输出并获取AI选择的位置
            output = new_stdout.getvalue().strip()
            sys.stdout = old_stdout

            try:
                move_position = int(output)
                # 构造并发送移动指令给机械臂
                message = f'2{computer_move_count}{move_position}'
                print(f"AI选择移动到位置 {move_position}")
                print(f"发送AI移动指令: {message}")
                send_message(message)  # 通过串口发送指令
                
                print("\nAI移动后的棋盘:")
                print_board(chess)
                
                # 检查AI是否获胜
                if winnerdetect(chess, 2):
                    print("\n🤖 AI获胜！")
                    print("游戏结束")
                    break
                
                # 检查是否平局
                if full(chess):
                    print("\n⚖️ 平局！")
                    print("游戏结束")
                    break
                    
                print("\n等待人类玩家下一步移动...")
                
            except (ValueError, IndexError) as e:
                print(f"错误：AI算法输出异常 - {e}")
                print("程序终止")
                break
            except Exception as e:
                print(f"错误：串口通信失败 - {e}")
                print("请检查串口连接")
                break

if __name__ == "__main__":
    """
    程序主入口
    
    异常处理：
    - 捕获键盘中断(Ctrl+C)
    - 处理系统异常
    - 确保程序优雅退出
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断程序执行")
        print("程序已安全退出")
    except Exception as e:
        print(f"\n程序运行时发生未预期的错误: {e}")
        print("请检查系统配置和硬件连接")
        print("程序已退出")
    finally:
        print("\n感谢使用三子棋AI系统！")
