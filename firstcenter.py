#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三子棋AI系统 - 中心位置控制模块

本模块用于控制机械臂在棋盘中心位置(位置4)放置棋子的专用程序。
主要功能：
- 获取用户输入的第一步棋子位置
- 自动设置第二步为中心位置(位置4)
- 通过摄像头显示棋盘区域
- 发送控制指令给机械臂

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

使用说明：
1. 运行程序后输入第一步黑棋位置(0-8)
2. 程序自动将第二步设为中心位置4
3. 按Enter键发送指令给机械臂
4. 再次按Enter键退出程序
"""

import cv2
from communication import send_message

# 初始化摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 设置摄像头宽度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 设置摄像头高度

# 按键计数器，用于控制程序流程
key_count = 0

# 获取用户输入的棋子位置
a = input("enter black1first: ")  # 第一步黑棋位置(0-8)
b = 4                             # 第二步固定为中心位置4

# 主程序循环
while True:
    # 读取摄像头画面
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    # 定义棋盘区域的ROI(感兴趣区域)
    roi_x, roi_y, roi_w, roi_h = 250, 200, 175, 175  # x坐标, y坐标, 宽度, 高度
    # 在画面上绘制红色矩形框标识棋盘区域
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 0, 255), 3)

    # 显示摄像头画面
    cv2.imshow('Camera', frame)
    # 检测按键输入
    key = cv2.waitKey(1) & 0xFF

    # 当按下Enter键时执行相应操作
    if key == 13:  # Enter键的ASCII码为13
        if key_count == 0:
            # 第一次按Enter：发送黑棋移动指令
            # 消息格式：'2' + 第一步位置 + 第二步位置(中心位置4)
            message = f'2{a}{b}'
            print(f"发送黑棋移动指令: {message}")
            send_message(message)  # 通过串口发送指令给机械臂
            key_count += 1
            print("指令已发送，再次按Enter键退出程序")
        else:
            # 第二次按Enter：退出程序
            print("程序结束")
            break

# 清理资源
print("正在释放摄像头资源...")
cap.release()           # 释放摄像头
cv2.destroyAllWindows() # 关闭所有OpenCV窗口
print("程序已安全退出")