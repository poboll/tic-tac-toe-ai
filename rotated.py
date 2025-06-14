#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三子棋AI系统 - 旋转棋盘标定模块

本模块用于在摄像头画面中显示旋转后的棋盘网格线，帮助用户进行棋盘位置标定。
主要功能：
- 在摄像头画面上绘制旋转的棋盘网格
- 实时显示四个关键点的连线
- 用于棋盘角度校正和位置确认

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

坐标系统：
- 使用四个关键点定义旋转后的棋盘区域
- 点的顺序：下中、右中、上中、左中
- 坐标基于640x480的摄像头分辨率

使用说明：
1. 运行程序查看旋转棋盘的网格线
2. 调整摄像头角度使实际棋盘与网格线对齐
3. 按'q'键退出程序
"""

import cv2

# 定义旋转棋盘的四个关键点坐标
# 这些坐标定义了一个旋转45度的菱形棋盘区域
points = [(338, 411),  # 下中点
          (461, 288),  # 右中点
          (338, 164),  # 上中点
          (214, 288)]  # 左中点

# 确保坐标值为整数类型
points = [(int(x), int(y)) for x, y in points]

# 初始化摄像头
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("错误：无法打开摄像头")
    print("请检查摄像头连接或权限设置")
    exit()

# 设置摄像头分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 设置摄像头宽度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 设置摄像头高度

print("旋转棋盘标定程序已启动")
print("红色网格线显示了旋转后的棋盘区域")
print("请调整摄像头角度使实际棋盘与网格线对齐")
print("按'q'键退出程序")

# 主程序循环 - 实时显示旋转棋盘网格
while True:
    # 读取摄像头画面
    ret, frame = cap.read()
    if not ret:
        print("错误：无法读取摄像头画面")
        break

    # 绘制旋转棋盘的网格线
    # 使用红色线条(BGR格式: (0, 0, 255))，线宽为3像素
    
    # 绘制外边框 - 连接四个关键点形成菱形
    cv2.line(frame, points[0], points[1], (0, 0, 255), 3)  # 下中 -> 右中
    cv2.line(frame, points[1], points[2], (0, 0, 255), 3)  # 右中 -> 上中
    cv2.line(frame, points[2], points[3], (0, 0, 255), 3)  # 上中 -> 左中
    cv2.line(frame, points[3], points[0], (0, 0, 255), 3)  # 左中 -> 下中
    
    # 绘制内部交叉线 - 形成3x3网格
    cv2.line(frame, points[0], points[2], (0, 0, 255), 3)  # 垂直中线：下中 -> 上中
    cv2.line(frame, points[1], points[3], (0, 0, 255), 3)  # 水平中线：右中 -> 左中
    
    # 显示带有网格线的摄像头画面
    cv2.imshow('Rotated Tic-Tac-Toe Grid Calibration', frame)

    # 检测按键输入
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # 按下'q'键退出
        print("用户请求退出程序")
        break
    elif key == ord('r'):  # 按下'r'键重置(可选功能)
        print("网格显示正常")

# 清理资源
print("正在释放摄像头资源...")
cap.release()           # 释放摄像头
cv2.destroyAllWindows() # 关闭所有OpenCV窗口
print("旋转棋盘标定程序已安全退出")