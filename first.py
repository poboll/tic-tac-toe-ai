#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
井字棋AI对战系统 - 第一玩家主程序

本程序作为井字棋游戏的第一玩家（人类玩家）主控程序，负责：
- 通过摄像头实时检测人类玩家的棋子放置
- 处理游戏逻辑和状态管理
- 触发AI玩家的移动决策
- 通过串口通信控制机械臂执行AI移动
- 检测游戏结束条件（获胜/平局）

系统架构:
1. 视觉检测模块：实时捕获和分析摄像头图像
2. 游戏逻辑模块：处理移动、检测获胜条件
3. 通信模块：与机械臂进行串口通信
4. AI决策模块：使用Minimax算法计算最优移动

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

使用说明:
1. 确保摄像头正确连接并校准
2. 确保串口设备正确连接
3. 运行程序后，人类玩家先手
4. 在摄像头视野内放置白色棋子
5. AI会自动计算并执行移动
"""

# 导入游戏决策相关函数
from decision import init_board, print_board, computermove, humanmove, winnerdetect, full
# 导入视觉检测模块
from versionfirst import capture_and_process_image
# 导入串口通信模块
from communication import send_message
# 导入系统模块用于输出重定向
import io
import sys

def main():
    """
    井字棋游戏主控制循环
    
    此函数实现了完整的游戏流程，包括：
    1. 初始化游戏状态
    2. 循环检测人类玩家移动
    3. 处理AI玩家响应
    4. 检测游戏结束条件
    5. 通过串口发送控制指令
    
    游戏流程:
    - 人类玩家先手，使用白色棋子
    - AI玩家后手，使用黑色棋子（由机械臂放置）
    - 实时检测作弊行为
    - 自动判断游戏结果
    
    通信协议:
    - 格式: "2{移动序号}{位置}"
    - 示例: "214" 表示第1次移动到位置4
    
    异常处理:
    - 自动处理视觉检测失败
    - 检测并阻止作弊行为
    - 处理串口通信异常
    """
    print("[系统] 井字棋AI对战系统启动")
    print("[系统] 人类玩家使用白色棋子，AI使用黑色棋子")
    print("[系统] 请在摄像头视野内放置棋子...\n")
    
    # 初始化游戏状态
    chess = init_board()  # 创建空棋盘
    detected_positions = set()  # 记录已检测到的棋子位置
    print_board(chess)  # 显示初始棋盘
    computer_move_count = 0  # AI移动计数器
    
    print("[游戏] 游戏开始，等待人类玩家移动...")
    
    # 主游戏循环
    while True:
        # 步骤1: 通过视觉检测捕获人类玩家的移动
        print("[检测] 正在检测新的棋子...")
        move = capture_and_process_image(detected_positions)
        
        if move is not None:
            print(f"[检测] 检测到人类玩家在位置 {move[0]} 放置棋子")
            
            # 步骤2: 处理人类玩家移动并检测作弊
            chess, position_changed = humanmove(chess, move[0], detected_positions)
            print_board(chess)
            
            # 步骤3: 检查人类玩家是否获胜
            if winnerdetect(chess, 1):
                print("\n🎉 [游戏结束] 人类玩家获胜！")
                print("[系统] 恭喜您战胜了AI！")
                break
            
            # 步骤4: 检查是否平局
            if full(chess):
                print("\n🤝 [游戏结束] 平局！")
                print("[系统] 双方实力相当，不分胜负！")
                break

            # 步骤5: 如果没有作弊，执行AI移动
            if not position_changed:
                print("\n[AI] 轮到AI移动...")
                computer_move_count += 1
                
                # 重定向stdout以捕获AI移动的输出
                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout

                # 执行AI移动计算
                chess = computermove(chess)

                # 恢复stdout并获取AI选择的位置
                output = new_stdout.getvalue().strip()
                sys.stdout = old_stdout

                # 解析AI移动位置
                try:
                    move_position = int(output)
                    print(f"[AI] AI选择位置: {move_position}")
                    
                    # 构造并发送控制消息
                    message = f'2{computer_move_count}{move_position}'
                    print(f"[通信] 发送控制指令: {message}")
                    send_message(message)
                    
                except ValueError:
                    print(f"[错误] 无法解析AI移动输出: {output}")
                    continue

                # 显示更新后的棋盘
                print_board(chess)
                
                # 步骤6: 检查AI是否获胜
                if winnerdetect(chess, 2):
                    print("\n🤖 [游戏结束] AI获胜！")
                    print("[系统] AI展现了强大的计算能力！")
                    break
                    
                # 步骤7: 再次检查是否平局
                if full(chess):
                    print("\n🤝 [游戏结束] 平局！")
                    print("[系统] 双方实力相当，不分胜负！")
                    break
            else:
                print("[警告] 检测到作弊行为，请重新放置棋子")
                print("[提示] 请在空位放置新棋子，不要移动已有棋子")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[系统] 用户中断，游戏结束")
    except Exception as e:
        print(f"\n[错误] 程序运行出现异常: {e}")
        print("[系统] 请检查摄像头和串口连接")
    finally:
        print("[系统] 程序退出")