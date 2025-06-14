#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三子棋AI系统 - 第二玩家计算机视觉检测模块

本模块专门用于检测黑棋(第二玩家)的棋子放置。
主要功能：
- 通过摄像头捕获棋盘图像
- 使用图像处理技术检测圆形棋子
- 识别黑色棋子并确定其在3x3网格中的位置
- 防止重复检测同一位置的棋子

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

技术特点：
- 使用霍夫圆检测算法识别棋子
- 采用自适应阈值和形态学操作优化图像
- 通过随机采样判断棋子颜色(白色/黑色)
- ROI(感兴趣区域)技术提高检测精度

检测流程：
1. 捕获摄像头画面并定义ROI区域
2. 图像预处理(灰度化、二值化、腐蚀)
3. 霍夫圆检测找到圆形物体
4. 颜色识别确定棋子类型
5. 坐标转换到3x3网格位置

与versionfirst.py的区别：
- versionfirst.py检测白棋(第一玩家)
- versionsecond.py检测黑棋(第二玩家)
"""

import cv2
import numpy as np
import random


def capture_and_process_image(detected_positions):
    """
    捕获并处理图像以检测黑棋位置
    
    本函数是第二玩家(人类)的棋子检测核心函数，专门检测黑色棋子。
    
    参数:
        detected_positions (set): 已检测到的棋子位置集合，用于避免重复检测
    
    返回:
        tuple: (位置, 颜色) 如果检测到新的黑棋
        None: 如果未检测到新的黑棋或检测失败
    
    检测原理:
    1. 图像预处理：灰度化 -> 二值化 -> 自适应阈值 -> 形态学腐蚀
    2. 霍夫圆检测：检测圆形物体(棋子)
    3. 颜色判断：通过随机采样判断是否为黑色棋子
    4. 位置映射：将像素坐标转换为3x3网格位置(0-8)
    
    异常处理:
    - 摄像头打开失败
    - 图像读取失败
    - 圆检测算法异常
    """
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return None
    
    # 读取一帧图像
    ret, frame = cap.read()
    if not ret:
        print("错误：无法读取摄像头画面")
        cap.release()
        return None
    
    # 定义感兴趣区域(ROI) - 棋盘区域
    # 坐标格式：(x起始, y起始, 宽度, 高度)
    roi_x, roi_y, roi_w, roi_h = 100, 100, 400, 400
    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]  # 裁剪ROI区域
    
    # 图像预处理步骤1：转换为灰度图像
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # 图像预处理步骤2：自适应阈值处理
    # 参数说明：最大值255，高斯自适应，二值化，块大小11，常数2
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # 图像预处理步骤3：形态学操作清理图像
    kernel = np.ones((3,3), np.uint8)  # 3x3卷积核
    thresh = cv2.erode(thresh, kernel, iterations=1)  # 腐蚀操作，去除噪点
    
    # 霍夫圆检测算法检测圆形棋子
    # 参数：图像，检测方法，分辨率比例，最小圆心距离，边缘检测阈值，累加器阈值，最小半径，最大半径
    circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, dp=1, minDist=30, param1=50, param2=30, minRadius=10, maxRadius=50)
    
    # 如果检测到圆形物体
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")  # 圆形参数取整
        
        # 遍历每个检测到的圆
        for (x, y, r) in circles:
            # 检查圆是否完全在ROI边界内
            if x - r >= 0 and y - r >= 0 and x + r < roi_w and y + r < roi_h:
                # 颜色识别：在圆周围采样像素点判断颜色
                sample_points = []
                for angle in range(0, 360, 30):  # 每30度采样一个点
                    # 计算采样点坐标(在圆的边缘内侧)
                    sample_x = int(x + (r - 5) * np.cos(np.radians(angle)))
                    sample_y = int(y + (r - 5) * np.sin(np.radians(angle)))
                    # 确保采样点在ROI范围内
                    if 0 <= sample_x < roi_w and 0 <= sample_y < roi_h:
                        sample_points.append(roi[sample_y, sample_x])
                
                # 如果成功采集到样本点
                if sample_points:
                    # 计算平均颜色值
                    avg_color = np.mean(sample_points, axis=0)
                    
                    # 根据亮度判断棋子颜色
                    brightness = np.mean(avg_color)
                    
                    if brightness > 150:  # 亮度阈值150，高于此值认为是白棋
                        color = "white"
                    else:  # 低于阈值认为是黑棋
                        color = "black"
                    
                    # 坐标转换：将像素坐标转换为3x3网格位置(0-8)
                    grid_x = int((x + roi_x) // (roi_w // 3))  # 计算网格列(0-2)
                    grid_y = int((y + roi_y) // (roi_h // 3))  # 计算网格行(0-2)
                    position = grid_y * 3 + grid_x  # 转换为线性位置(0-8)
                    
                    # 检查条件：位置未被检测过 且 是黑色棋子(第二玩家)
                    if position not in detected_positions and color == "black":
                        cap.release()  # 释放摄像头资源
                        return position, color  # 返回检测结果
    
    # 未检测到符合条件的棋子
    cap.release()  # 释放摄像头资源
    return None  # 返回空值