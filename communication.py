#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
串口通信模块 - 2024电赛E题三子棋AI系统

本模块负责与机械臂或其他外部设备的串口通信，实现指令的发送和数据的接收。
支持多平台串口配置，包括树莓派GPIO、USB转串口、Windows COM口等。

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)
"""

import serial
import serial.tools.list_ports

# ==================== 串口配置 ====================
# 根据不同平台选择合适的串口配置

# 树莓派GPIO串口配置（推荐用于嵌入式系统）
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)

# 其他平台串口配置选项（取消注释以使用）
# ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)    # Linux USB转串口
# ser = serial.Serial(1, 9600, timeout=0.5)                # Windows COM1（数字形式）
# ser = serial.Serial("COM1", 9600, timeout=0.5)           # Windows COM1（字符串形式）
# ser = serial.Serial("/dev/ttyS1", 9600, timeout=0.5)     # Linux标准串口

# ==================== 核心通信函数 ====================

def send_message(message):
    """
    发送指令消息到串口设备
    
    本函数将游戏指令封装成标准帧格式后通过串口发送给机械臂或其他控制设备。
    帧格式: [帧头高][帧头低][数据内容][帧尾]
    
    参数:
        message (str): 要发送的指令字符串
                      格式示例: "210" (指令类型2, 起始位置1, 目标位置0)
    
    指令编码说明:
        1XY - 白棋移动指令 (X=起始位置, Y=目标位置)
        2XY - 黑棋移动指令 (X=起始位置, Y=目标位置) 
        3XY - 悔棋检测指令 (X=原位置, Y=新位置)
        4XY - 旋转校准指令 (X=校准参数1, Y=校准参数2)
        5XY - 扩展功能指令 (X=功能码, Y=参数)
    
    返回:
        None
    
    异常:
        serial.SerialException: 串口通信异常
    """
    # 定义通信协议的帧结构标识字节
    frame_header_high = 0xAA  # 帧头高字节 - 标识帧开始
    frame_header_low = 0x55   # 帧头低字节 - 与高字节组成帧头
    frame_tail = 0x9A         # 帧尾字节 - 标识帧结束

    # 将字符串指令转换为字节数组，使用UTF-8编码
    message_bytes = message.encode('utf-8')
    
    # 构建完整的数据帧
    frame = bytearray()
    frame.append(frame_header_high)  # 添加帧头高字节
    frame.append(frame_header_low)   # 添加帧头低字节
    frame.extend(message_bytes)      # 添加实际数据内容
    frame.append(frame_tail)         # 添加帧尾字节

    try:
        # 通过串口发送完整数据帧
        ser.write(frame)
        print(f"[通信] 发送指令: {message} -> 帧数据: {' '.join(f'{b:02X}' for b in frame)}")
    except serial.SerialException as e:
        print(f"[错误] 串口发送失败: {e}")
    except Exception as e:
        print(f"[错误] 发送消息时发生未知错误: {e}")

def receive_data(serial_obj, receive_mode=1):
    """
    从串口接收数据的通用函数
    
    本函数提供两种数据接收模式：逐字节接收和整体接收。
    主要用于接收机械臂的状态反馈或确认信息。
    
    参数:
        serial_obj: 串口对象实例
        receive_mode (int): 接收模式
                           0 - 逐字节接收模式（适用于调试）
                           1 - 整体接收模式（推荐用于正常通信）
    
    返回:
        None (数据通过print输出)
    
    注意:
        此函数包含无限循环，建议在独立线程中运行
    """
    print("[通信] 开始接收数据，模式:", "逐字节" if receive_mode == 0 else "整体接收")
    
    while True:
        try:
            # 检查是否有待接收的数据
            if serial_obj.in_waiting > 0:
                
                if receive_mode == 0:
                    # 模式0: 逐字节接收（用于调试和详细分析）
                    for i in range(serial_obj.in_waiting):
                        # 读取单个字节
                        byte_data = serial_obj.read(1)
                        print(f"[接收] ASCII数据: {byte_data}")
                        
                        # 转换为十六进制显示
                        hex_data = byte_data.hex().upper()
                        # 转换为十进制显示
                        dec_data = int(hex_data, 16) if hex_data else 0
                        print(f"[接收] 十六进制: {hex_data}, 十进制: {dec_data}")
                        
                elif receive_mode == 1:
                    # 模式1: 整体接收（推荐模式）
                    try:
                        # 方式一：指定字节数接收并解码
                        # data = serial_obj.read(serial_obj.in_waiting).decode("utf-8")
                        
                        # 方式二：读取所有可用数据
                        data = serial_obj.read_all()
                        print(f"[接收] 完整数据: {data}")
                        
                        # 如果是文本数据，尝试解码
                        if data:
                            try:
                                decoded_data = data.decode('utf-8')
                                print(f"[接收] 解码文本: {decoded_data}")
                            except UnicodeDecodeError:
                                print(f"[接收] 二进制数据: {data.hex().upper()}")
                                
                    except Exception as decode_error:
                        print(f"[错误] 数据解码失败: {decode_error}")
                        
        except serial.SerialException as e:
            print(f"[错误] 串口接收异常: {e}")
            break
        except Exception as e:
            print(f"[错误] 接收数据时发生未知错误: {e}")
            break

def print_used_com(serial_obj):
    """
    打印当前使用的串口设备详细信息
    
    此函数用于显示当前串口连接的所有配置参数，
    便于调试和确认连接设置是否正确。
    
    参数:
        serial_obj: 串口对象实例
    
    返回:
        None (信息通过print输出)
    """
    print("\n=== 串口设备详细信息 ===")
    print(f"串口名称: {serial_obj.name}")
    print(f"波特率: {serial_obj.baudrate} bps")
    print(f"数据位: {serial_obj.bytesize} bits")
    print(f"校验位: {serial_obj.parity}")
    print(f"停止位: {serial_obj.stopbits}")
    print(f"超时时间: {serial_obj.timeout} 秒")
    print(f"连接状态: {'已连接' if serial_obj.is_open else '未连接'}")
    print("========================\n")

def print_available_com():
    """
    扫描并打印系统中所有可用的串口设备
    
    此函数会自动检测系统中所有可用的串口设备，
    包括USB转串口、蓝牙串口等，并显示设备名称和描述信息。
    在连接设备前调用此函数可以帮助确定正确的串口名称。
    
    返回:
        None (设备列表通过print输出)
    
    示例输出:
        可用的串口设备:
        /dev/ttyUSB0 - USB Serial Device
        /dev/ttyACM0 - Arduino Uno
    """
    try:
        # 获取系统中所有串口设备
        port_list = list(serial.tools.list_ports.comports())
        
        print("\n=== 可用串口设备扫描 ===")
        if port_list:
            print(f"发现 {len(port_list)} 个可用串口设备:")
            for i, port in enumerate(port_list, 1):
                port_info = list(port)
                port_name = port_info[0]  # 串口名称
                port_desc = port_info[1]  # 设备描述
                print(f"  {i}. {port_name} - {port_desc}")
        else:
            print("未发现可用的串口设备")
            print("请检查:")
            print("  1. 设备是否正确连接")
            print("  2. 驱动程序是否已安装")
            print("  3. 设备是否被其他程序占用")
        print("=========================\n")
        
    except Exception as e:
        print(f"[错误] 扫描串口设备时发生错误: {e}")

def open_engine(serial_obj):
    """
    打开串口连接
    
    此函数用于建立与指定串口设备的连接。
    在发送或接收数据前必须先调用此函数。
    
    参数:
        serial_obj: 串口对象实例
    
    返回:
        bool: 连接是否成功建立
    
    异常:
        serial.SerialException: 串口打开失败时抛出
    """
    try:
        serial_obj.open()
        is_connected = serial_obj.is_open
        print(f"[连接] 串口连接状态: {'成功' if is_connected else '失败'}")
        return is_connected
    except serial.SerialException as e:
        print(f"[错误] 无法打开串口: {e}")
        return False
    except Exception as e:
        print(f"[错误] 打开串口时发生未知错误: {e}")
        return False

def close_engine(serial_obj):
    """
    关闭串口连接
    
    此函数用于安全地关闭串口连接，释放系统资源。
    程序结束前或切换串口设备时应调用此函数。
    
    参数:
        serial_obj: 串口对象实例
    
    返回:
        bool: 连接是否成功关闭
    """
    try:
        if serial_obj.is_open:
            serial_obj.close()
        is_closed = not serial_obj.is_open
        print(f"[连接] 串口关闭状态: {'成功' if is_closed else '失败'}")
        return is_closed
    except Exception as e:
        print(f"[错误] 关闭串口时发生错误: {e}")
        return False

def read_size(serial_obj, size):
    """
    从串口读取指定字节数的数据
    
    此函数会尝试从串口读取指定数量的字节。
    如果设置了超时时间，可能返回少于指定字节数的数据。
    
    参数:
        serial_obj: 串口对象实例
        size (int): 要读取的字节数
    
    返回:
        bytes: 读取到的数据，可能少于指定的字节数
    
    注意:
        - 如果没有设置超时，函数会一直等待直到读取到指定字节数
        - 建议设置合理的超时时间避免程序阻塞
    """
    try:
        data = serial_obj.read(size)
        print(f"[读取] 请求 {size} 字节，实际读取 {len(data)} 字节")
        return data
    except Exception as e:
        print(f"[错误] 读取数据时发生错误: {e}")
        return b''

def read_line(serial_obj, encoding='utf-8'):
    """
    从串口读取一行数据（直到遇到换行符）
    
    此函数会读取数据直到遇到换行符('\n')为止，
    并自动进行字符编码转换。
    
    参数:
        serial_obj: 串口对象实例
        encoding (str): 字符编码格式，默认为'utf-8'
                       常用编码: 'utf-8', 'gbk', 'ascii'
    
    返回:
        str: 解码后的字符串数据（不包含换行符）
    
    异常:
        UnicodeDecodeError: 解码失败时抛出
    """
    try:
        # 读取一行数据
        raw_data = serial_obj.readline()
        
        # 尝试使用指定编码解码
        try:
            decoded_data = raw_data.decode(encoding).strip()
            print(f"[读行] 使用 {encoding} 编码成功解码: {decoded_data}")
            return decoded_data
        except UnicodeDecodeError:
            # 如果指定编码失败，尝试其他常用编码
            for fallback_encoding in ['gbk', 'ascii', 'latin1']:
                if fallback_encoding != encoding:
                    try:
                        decoded_data = raw_data.decode(fallback_encoding).strip()
                        print(f"[读行] 使用备用编码 {fallback_encoding} 解码成功: {decoded_data}")
                        return decoded_data
                    except UnicodeDecodeError:
                        continue
            
            # 所有编码都失败，返回原始十六进制数据
            print(f"[警告] 无法解码数据，返回十六进制: {raw_data.hex()}")
            return raw_data.hex()
            
    except Exception as e:
        print(f"[错误] 读取行数据时发生错误: {e}")
        return ""

def send_data(serial_obj, data):
    """
    向串口发送原始数据
    
    此函数用于发送字节数据到串口设备。
    与send_message函数不同，此函数不添加帧头帧尾。
    
    参数:
        serial_obj: 串口对象实例
        data (bytes): 要发送的字节数据
    
    返回:
        int: 实际发送的字节数，-1表示发送失败
    
    注意:
        如果需要发送带协议帧的数据，请使用send_message函数
    """
    try:
        if isinstance(data, str):
            # 如果输入是字符串，转换为字节
            data = data.encode('utf-8')
        
        bytes_written = serial_obj.write(data)
        print(f"[发送] 原始数据发送成功，字节数: {bytes_written}")
        return bytes_written
        
    except Exception as e:
        print(f"[错误] 发送原始数据时发生错误: {e}")
        return -1