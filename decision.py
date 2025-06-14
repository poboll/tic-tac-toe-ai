from communication import send_message
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
井字棋游戏决策模块

本模块实现了井字棋游戏的核心逻辑，包括：
- 游戏棋盘的初始化和显示
- 人类玩家和AI玩家的移动逻辑
- 使用Minimax算法的AI决策
- 游戏胜负判断和防作弊检测

作者: poboll
邮箱: caiths@icloud.com
许可证: MIT License (2023)

棋盘表示:
- 0: 空位
- 1: 人类玩家 (X)
- 2: AI玩家 (O)

坐标系统:
0 1 2
3 4 5
6 7 8
"""

def init_board():
    """
    初始化3x3井字棋棋盘
    
    创建一个空的3x3棋盘，所有位置初始化为0（空位）。
    这是每局游戏开始时的标准棋盘状态。
    
    返回:
        list: 3x3的二维列表，所有元素为0
        
    示例:
        >>> board = init_board()
        >>> print(board)
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    """
    return [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

def print_board(chess):
    """
    在控制台打印当前棋盘状态
    
    将棋盘以可视化的方式显示在控制台中，
    使用符号表示不同的棋子状态。
    
    参数:
        chess (list): 3x3的棋盘状态列表
                     0-空位(.), 1-人类玩家(X), 2-AI玩家(O)
    
    返回:
        None (直接打印到控制台)
        
    示例输出:
        . X .
        O . X
        . O .
    """
    # 定义棋子符号映射
    symbols = {0: '.', 1: 'X', 2: 'O'}
    
    print("\n=== 当前棋盘状态 ===")
    for i, row in enumerate(chess):
        # 打印每一行，用空格分隔符号
        row_display = ' '.join(symbols[cell] for cell in row)
        print(f"{i}: {row_display}")
    print("==================\n")

def humanmove(chess, i, detected_positions):
    """
    处理人类玩家的移动并检测作弊行为
    
    此函数负责在棋盘上放置人类玩家的棋子，并检测是否存在
    移动已有棋子的作弊行为。如果检测到作弊，会发送警告消息
    并撤销该移动。
    
    参数:
        chess (list): 当前的3x3棋盘状态
        i (int): 移动位置的索引 (0-8)
                0-2: 第一行, 3-5: 第二行, 6-8: 第三行
        detected_positions (list): 当前检测到的棋子位置列表
    
    返回:
        tuple: (更新后的棋盘, 是否检测到作弊)
               - chess (list): 更新后的棋盘状态
               - is_cheating (bool): True表示检测到作弊，False表示正常移动
    
    作弊检测逻辑:
        1. 记录移动前所有人类棋子的位置
        2. 执行移动操作
        3. 检查是否有棋子位置发生了变化
        4. 如果有位置变化，判定为作弊并撤销移动
    
    通信协议:
        作弊检测时发送消息格式: "3{原位置}{新位置}"
        例如: "304" 表示棋子从位置0移动到位置4
    """
    # 记录移动前所有人类玩家棋子的位置
    # 创建位置映射：检测位置 -> 棋盘索引
    original_positions = {
        pos: (row * 3 + col) 
        for row in range(3) 
        for col in range(3) 
        for pos in detected_positions 
        if chess[row][col] == 1
    }
    
    print(f"[移动] 人类玩家尝试在位置 {i} 放置棋子")
    
    # 根据索引在棋盘上放置人类玩家的棋子 (标记为1)
    if 0 <= i <= 2:
        # 第一行 (行索引0)
        chess[0][i] = 1
    elif 3 <= i <= 5:
        # 第二行 (行索引1)
        chess[1][i - 3] = 1
    elif 6 <= i <= 8:
        # 第三行 (行索引2)
        chess[2][i - 6] = 1
    else:
        print(f"[错误] 无效的移动位置: {i}")
        return chess, False

    # 记录移动后所有人类玩家棋子的位置
    new_positions = {
        pos: (row * 3 + col) 
        for row in range(3) 
        for col in range(3) 
        for pos in detected_positions 
        if chess[row][col] == 1
    }
    
    # 检测作弊：比较移动前后的位置变化
    for pos in original_positions:
        if pos in new_positions and original_positions[pos] != new_positions[pos]:
            # 发现棋子位置发生变化，判定为作弊
            old_pos = original_positions[pos]
            new_pos = new_positions[pos]
            
            print(f"[警告] 检测到作弊行为！棋子从位置 {old_pos} 移动到位置 {new_pos}")
            
            # 构造并发送作弊警告消息
            cheat_message = f"3{old_pos}{new_pos}"
            print(f"[通信] 发送作弊警告: {cheat_message}")
            send_message(cheat_message)
            
            # 撤销当前移动，恢复棋盘状态
            print(f"[系统] 撤销非法移动，恢复位置 {i}")
            if 0 <= i <= 2:
                chess[0][i] = 0
            elif 3 <= i <= 5:
                chess[1][i - 3] = 0
            elif 6 <= i <= 8:
                chess[2][i - 6] = 0
                
            return chess, True  # 返回作弊标志
    
    print(f"[移动] 人类玩家在位置 {i} 的移动有效")
    return chess, False  # 正常移动，无作弊

def computermove(chess, first_move=None):
    """
    AI玩家进行移动决策
    
    使用Minimax算法计算最优移动位置。如果是游戏的第一步，
    可以指定特定位置；否则通过算法自动选择最佳位置。
    
    参数:
        chess (list): 当前的3x3棋盘状态
        first_move (int, optional): 指定的第一步移动位置 (0-8)
                                   如果为None，则使用Minimax算法计算
    
    返回:
        list: 更新后的棋盘状态，包含AI的新移动
    
    算法说明:
        1. 如果指定了first_move，直接在该位置放置AI棋子
        2. 否则遍历所有可能的移动位置
        3. 对每个位置使用Minimax算法评估得分
        4. 选择得分最高的位置作为最终移动
    
    Minimax评分系统:
        +1: AI获胜
        -1: 人类获胜
         0: 平局
    """
    # 如果指定了第一步移动位置，直接执行
    if first_move is not None:
        print(f"[AI移动] 执行指定的第一步移动: 位置 {first_move}")
        row, col = divmod(first_move, 3)  # 将索引转换为行列坐标
        chess[row][col] = 2  # 在指定位置放置AI棋子
        return chess

    print("[AI移动] 开始计算最优移动位置...")
    
    # 初始化最佳移动搜索
    best_score = -float('inf')  # 最佳得分，初始为负无穷
    best_move = None            # 最佳移动位置
    
    # 遍历棋盘上所有可能的移动位置
    for i in range(9):
        row, col = divmod(i, 3)  # 将索引转换为行列坐标
        
        # 只考虑空位
        if chess[row][col] == 0:
            # 尝试在该位置放置AI棋子
            chess[row][col] = 2
            
            # 使用Minimax算法评估这个移动的得分
            # depth=0: 当前深度, False: 下一步是人类玩家的回合
            score = minimax(chess, 0, False)
            
            # 撤销试探性移动
            chess[row][col] = 0
            
            # 更新最佳移动
            if score > best_score:
                best_score = score
                best_move = (row, col)
                print(f"[AI分析] 位置 {i} 得分: {score} (当前最佳)")
            else:
                print(f"[AI分析] 位置 {i} 得分: {score}")
    
    # 执行最佳移动
    if best_move is not None:
        chess[best_move[0]][best_move[1]] = 2
        move_index = best_move[0] * 3 + best_move[1]
        print(f"[AI移动] 选择位置 {move_index}，预期得分: {best_score}")
    else:
        print("[错误] 未找到有效的移动位置")
    
    return chess
def minimax(chess, depth, is_maximizing):
    """
    Minimax算法实现 - AI决策的核心算法
    
    这是一个递归算法，用于在零和游戏中找到最优策略。
    算法会模拟所有可能的游戏路径，并为每个位置计算最优得分。
    
    参数:
        chess (list): 当前棋盘状态
        depth (int): 当前搜索深度（递归层数）
        is_maximizing (bool): 当前是否为最大化玩家（AI）的回合
                             True: AI回合（寻求最大得分）
                             False: 人类回合（寻求最小得分）
    
    返回:
        int: 当前棋盘状态的评估得分
             +1: AI获胜的局面
             -1: 人类获胜的局面
              0: 平局的局面
    
    算法原理:
        1. 终止条件检查：游戏结束时返回相应得分
        2. 最大化层（AI回合）：选择得分最高的移动
        3. 最小化层（人类回合）：选择得分最低的移动
        4. 递归搜索所有可能的移动路径
    
    时间复杂度: O(b^d)，其中b是分支因子，d是搜索深度
    空间复杂度: O(d)，递归调用栈的深度
    """
    # 终止条件1：AI获胜
    if winnerdetect(chess, 2):
        return 1  # AI获胜，返回正分
    
    # 终止条件2：人类获胜
    if winnerdetect(chess, 1):
        return -1  # 人类获胜，返回负分
    
    # 终止条件3：棋盘已满（平局）
    if full(chess):
        return 0  # 平局，返回零分

    if is_maximizing:
        # 最大化层：AI的回合，寻求最高得分
        best_score = -float('inf')
        
        # 尝试所有可能的移动位置
        for i in range(9):
            row, col = divmod(i, 3)
            
            # 只考虑空位
            if chess[row][col] == 0:
                # 试探性地放置AI棋子
                chess[row][col] = 2
                
                # 递归调用，切换到最小化层（人类回合）
                score = minimax(chess, depth + 1, False)
                
                # 撤销试探性移动
                chess[row][col] = 0
                
                # 更新最佳得分（选择最大值）
                best_score = max(score, best_score)
        
        return best_score
    
    else:
        # 最小化层：人类的回合，寻求最低得分
        best_score = float('inf')
        
        # 尝试所有可能的移动位置
        for i in range(9):
            row, col = divmod(i, 3)
            
            # 只考虑空位
            if chess[row][col] == 0:
                # 试探性地放置人类棋子
                chess[row][col] = 1
                
                # 递归调用，切换到最大化层（AI回合）
                score = minimax(chess, depth + 1, True)
                
                # 撤销试探性移动
                chess[row][col] = 0
                
                # 更新最佳得分（选择最小值）
                best_score = min(score, best_score)
        
        return best_score

def winnerdetect(chess, player):
    """
    检测指定玩家是否获胜
    
    检查棋盘上是否存在三子连线的获胜条件。
    井字棋的获胜条件包括：横线、竖线、对角线三子连成一线。
    
    参数:
        chess (list): 当前的3x3棋盘状态
        player (int): 要检测的玩家标识
                     1: 人类玩家 (X)
                     2: AI玩家 (O)
    
    返回:
        bool: True表示该玩家获胜，False表示未获胜
    
    获胜条件检测:
        1. 横线获胜：任意一行的三个位置都是该玩家的棋子
        2. 竖线获胜：任意一列的三个位置都是该玩家的棋子
        3. 对角线获胜：主对角线或副对角线的三个位置都是该玩家的棋子
    
    示例:
        >>> chess = [[1, 1, 1], [0, 2, 0], [2, 0, 2]]
        >>> winnerdetect(chess, 1)  # 检测人类玩家
        True  # 第一行三子连线
    """
    # 检测横线获胜：检查每一行是否三子连线
    for i, row in enumerate(chess):
        if all(cell == player for cell in row):
            print(f"[获胜检测] 玩家 {player} 在第 {i+1} 行获胜")
            return True
    
    # 检测竖线获胜：检查每一列是否三子连线
    for col in range(3):
        if all(chess[row][col] == player for row in range(3)):
            print(f"[获胜检测] 玩家 {player} 在第 {col+1} 列获胜")
            return True
    
    # 检测对角线获胜
    # 主对角线：左上到右下 (0,0) -> (1,1) -> (2,2)
    if all(chess[i][i] == player for i in range(3)):
        print(f"[获胜检测] 玩家 {player} 在主对角线获胜")
        return True
    
    # 副对角线：右上到左下 (0,2) -> (1,1) -> (2,0)
    if all(chess[i][2 - i] == player for i in range(3)):
        print(f"[获胜检测] 玩家 {player} 在副对角线获胜")
        return True
    
    # 未检测到获胜条件
    return False

def full(chess):
    """
    检测棋盘是否已满
    
    遍历整个棋盘，检查是否还有空位（值为0的位置）。
    如果棋盘已满且没有玩家获胜，则游戏结果为平局。
    
    参数:
        chess (list): 当前的3x3棋盘状态
    
    返回:
        bool: True表示棋盘已满，False表示还有空位
    
    用途:
        1. 判断游戏是否结束（平局条件）
        2. 在Minimax算法中作为终止条件
        3. 确定是否还有可用的移动位置
    
    示例:
        >>> chess = [[1, 2, 1], [2, 1, 2], [2, 1, 2]]
        >>> full(chess)
        True  # 棋盘已满
        
        >>> chess = [[1, 2, 0], [2, 1, 2], [2, 1, 2]]
        >>> full(chess)
        False  # 还有空位
    """
    # 遍历每一行
    for i, row in enumerate(chess):
        # 检查该行是否有空位（值为0）
        if any(cell == 0 for cell in row):
            print(f"[棋盘检测] 第 {i+1} 行还有空位")
            return False  # 发现空位，棋盘未满
    
    print("[棋盘检测] 棋盘已满，无可用位置")
    return True  # 所有位置都被占用，棋盘已满

