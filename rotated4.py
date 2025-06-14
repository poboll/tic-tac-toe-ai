#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三子棋AI系统 - 旋转棋盘四步序列控制模块

本模块用于在旋转棋盘上执行四步棋子移动序列，支持坐标映射转换。
主要功能：
- 获取用户输入的四步棋子位置(两步白棋 + 两步黑棋)
- 支持旋转棋盘的坐标映射转换
- 在摄像头画面上显示旋转棋盘的关键点
- 按顺序发送控制指令给机械臂

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

坐标映射系统：
- 标准棋盘位置: 0-8 (3x3网格，从左上到右下)
- 旋转棋盘映射: {2:0, 5:1, 8:2, 1:3, 7:5, 0:6, 6:8}
- 当global=1时启用坐标映射转换

通信协议：
- 白棋指令格式: '4' + 起始位置 + 目标位置
- 黑棋指令格式: '5' + 起始位置 + 目标位置

使用说明：
1. 输入global参数(1=启用旋转映射, 0=标准坐标)
2. 依次输入四步棋子移动位置
3. 按Enter键逐步执行每个移动指令
4. 程序会显示旋转棋盘的关键点并发送指令
"""

import cv2
from communication import send_message

# 按键计数器，用于跟踪当前执行到第几步
key_count = 0

# 获取用户输入参数
print("=== 旋转棋盘四步序列控制程序 ===")
high = int(input("global (1=启用旋转映射, 0=标准坐标): "))
print("\n请输入四步棋子移动序列:")
x = int(input("enter white1first: "))   # 第一步白棋起始位置
y = int(input("enter white1last: "))    # 第一步白棋目标位置
m = int(input("enter white2first: "))   # 第二步白棋起始位置
n = int(input("enter white2last: "))    # 第二步白棋目标位置
a = int(input("enter black1first: "))   # 第一步黑棋起始位置
b = int(input("enter black1last: "))    # 第一步黑棋目标位置
c = int(input("enter black2first: "))   # 第二步黑棋起始位置
d = int(input("enter black2last: "))    # 第二步黑棋目标位置

# 旋转棋盘的坐标映射表
# 将标准3x3网格位置映射到旋转45度后的位置
mapping = {
    2: 0,  # 标准位置2 -> 旋转位置0
    5: 1,  # 标准位置5 -> 旋转位置1
    8: 2,  # 标准位置8 -> 旋转位置2
    1: 3,  # 标准位置1 -> 旋转位置3
    # 位置4(中心)保持不变
    7: 5,  # 标准位置7 -> 旋转位置5
    0: 6,  # 标准位置0 -> 旋转位置6
    6: 8   # 标准位置6 -> 旋转位置8
}

# 根据global参数决定是否应用坐标映射
if high == 1:
    print("\n启用旋转坐标映射转换...")
    x = mapping.get(x, x)  # 如果x在映射表中则转换，否则保持原值
    y = mapping.get(y, y)
    m = mapping.get(m, m)
    n = mapping.get(n, n)
    a = mapping.get(a, a)
    b = mapping.get(b, b)
    c = mapping.get(c, c)
    d = mapping.get(d, d)
    print(f"坐标映射完成: 白棋({x},{y}),({m},{n}) 黑棋({a},{b}),({c},{d})")
else:
    print("\n使用标准坐标系统")

# 定义旋转棋盘的四个关键点坐标(用于显示)
points = [(338, 411),  # 下中点
          (461, 288),  # 右中点
          (338, 164),  # 上中点
          (214, 288)]  # 左中点
# 确保坐标值为整数类型
points = [(int(x), int(y)) for x, y in points]

# 初始化摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 设置摄像头宽度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 设置摄像头高度

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("错误：无法打开摄像头")
    print("请检查摄像头连接或权限设置")
    exit()

print("\n摄像头已启动，显示旋转棋盘关键点")
print("红色圆点标识了旋转棋盘的四个关键位置")
print("按Enter键开始执行四步移动序列...")

# 主程序循环 - 显示旋转棋盘并执行四步序列
while True:
    # 读取摄像头画面
    ret, frame = cap.read()
    if not ret:
        print("错误：无法读取摄像头画面")
        break

    # 在画面上绘制旋转棋盘的四个关键点
    for i, point in enumerate(points):
        # 绘制红色填充圆点，半径为5像素
        cv2.circle(frame, point, 5, (0, 0, 255), -1)
        # 在每个点旁边添加标签
        labels = ['下中', '右中', '上中', '左中']
        cv2.putText(frame, labels[i], (point[0] + 10, point[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 显示带有关键点的摄像头画面
    cv2.imshow('Rotated Tic-Tac-Toe Control', frame)
    # 检测按键输入
    key = cv2.waitKey(1) & 0xFF

    # 当按下Enter键时执行相应的移动指令
    if key == 13:  # Enter键的ASCII码为13
        if key_count == 0:
            # 第一步：执行第一个白棋移动(指令码4)
            message = f'4{x}{y}'  # 格式：'4' + 起始位置 + 目标位置
            print(f"步骤1 - 发送第一个白棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("第一步完成，按Enter键执行第二步...")
        elif key_count == 1:
            # 第二步：执行第二个白棋移动(指令码4)
            message = f'4{m}{n}'  # 格式：'4' + 起始位置 + 目标位置
            print(f"步骤2 - 发送第二个白棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("第二步完成，按Enter键执行第三步...")
        elif key_count == 2:
            # 第三步：执行第一个黑棋移动(指令码5)
            message = f'5{a}{b}'  # 格式：'5' + 起始位置 + 目标位置
            print(f"步骤3 - 发送第一个黑棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("第三步完成，按Enter键执行第四步...")
        elif key_count == 3:
            # 第四步：执行第二个黑棋移动(指令码5)
            message = f'5{c}{d}'  # 格式：'5' + 起始位置 + 目标位置
            print(f"步骤4 - 发送第二个黑棋移动指令: {message}")
            send_message(message)
            key_count += 1
            print("所有四步旋转棋盘移动序列已完成！按Enter键退出程序...")
        else:
            # 所有步骤完成，退出程序
            print("四步旋转棋盘序列执行完毕，程序结束")
            break

# 清理资源
print("正在释放摄像头资源...")
cap.release()           # 释放摄像头
cv2.destroyAllWindows() # 关闭所有OpenCV窗口
print("旋转棋盘控制程序已安全退出")