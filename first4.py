#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三子棋AI系统 - 四步棋序列控制模块

本模块用于控制机械臂执行预定义的四步棋子移动序列。
主要功能：
- 获取用户输入的四步棋子位置(两步白棋 + 两步黑棋)
- 按顺序发送控制指令给机械臂
- 通过摄像头实时显示棋盘区域
- 支持手动触发每一步的执行

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

通信协议：
- 白棋指令格式: '1' + 起始位置 + 目标位置
- 黑棋指令格式: '2' + 起始位置 + 目标位置
- 位置编号: 0-8 (3x3棋盘从左上到右下)

使用说明：
1. 依次输入两步白棋和两步黑棋的位置
2. 按Enter键逐步执行每个移动指令
3. 程序会按顺序发送四个指令给机械臂
"""

import cv2
from communication import send_message

# 获取用户输入的棋子移动序列
print("请输入四步棋子移动序列:")
x = input("enter white1first: ")   # 第一步白棋起始位置
y = input("enter white1last: ")    # 第一步白棋目标位置
m = input("enter white2first: ")   # 第二步白棋起始位置
n = input("enter white2last: ")    # 第二步白棋目标位置
a = input("enter black1first: ")   # 第一步黑棋起始位置
b = input("enter black1last: ")    # 第一步黑棋目标位置
c = input("enter black2first: ")   # 第二步黑棋起始位置
d = input("enter black2last: ")    # 第二步黑棋目标位置

# 初始化摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 设置摄像头宽度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 设置摄像头高度

# 按键计数器，用于跟踪当前执行到第几步
key_count = 0

print("\n摄像头已启动，按Enter键开始执行移动序列...")

# 主程序循环 - 四步棋序列执行
while True:
    # 读取摄像头画面
    ret, frame = cap.read()
    if not ret:
        print("错误：无法读取摄像头画面")
        break

    # 定义棋盘区域的ROI(感兴趣区域)
    roi_x, roi_y, roi_w, roi_h = 250, 200, 175, 175  # x坐标, y坐标, 宽度, 高度
    # 在画面上绘制红色矩形框标识棋盘区域
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 0, 255), 3)

    # 显示摄像头画面
    cv2.imshow('Camera', frame)
    # 检测按键输入
    key = cv2.waitKey(1) & 0xFF

    # 当按下Enter键时执行相应的移动指令
    if key == 13:  # Enter键的ASCII码为13
        if key_count == 0:
            # 第一步：执行第一个白棋移动
            message = f'1{x}{y}'  # 格式：'1' + 起始位置 + 目标位置
            print(f"步骤1 - 发送第一个白棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("第一步完成，按Enter键执行第二步...")
        elif key_count == 1:
            # 第二步：执行第二个白棋移动
            message = f'1{m}{n}'  # 格式：'1' + 起始位置 + 目标位置
            print(f"步骤2 - 发送第二个白棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("第二步完成，按Enter键执行第三步...")
        elif key_count == 2:
            # 第三步：执行第一个黑棋移动
            message = f'2{a}{b}'  # 格式：'2' + 起始位置 + 目标位置
            print(f"步骤3 - 发送第一个黑棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("第三步完成，按Enter键执行第四步...")
        elif key_count == 3:
            # 第四步：执行第二个黑棋移动
            message = f'2{c}{d}'  # 格式：'2' + 起始位置 + 目标位置
            print(f"步骤4 - 发送第二个黑棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("所有四步移动序列已完成！按Enter键退出程序...")
        else:
            # 所有步骤完成，退出程序
            print("四步棋序列执行完毕，程序结束")
            break

# 清理资源
print("正在释放摄像头资源...")
cap.release()           # 释放摄像头
cv2.destroyAllWindows() # 关闭所有OpenCV窗口
print("程序已安全退出")
