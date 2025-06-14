# 高鲁棒性三子棋AI视觉检测系统

> **2024年全国大学生电子设计竞赛E题开源方案**  
> 基于OpenCV的高精度棋盘棋子检测与智能对弈系统

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Competition](https://img.shields.io/badge/Competition-2024电赛E题-red.svg)]()

## 🎬 演示视频

> **系统运行演示**：展示三子棋AI系统的完整工作流程，包括视觉检测、AI决策和机械臂控制

[![演示视频](https://img.shields.io/badge/🎥_演示视频-点击观看-blue.svg)](https://github.com/poboll/tic-tac-toe-ai/releases/tag/v1.0.0)

**视频内容包括：**
- 🎯 棋盘校准与坐标映射
- 👁️ 实时棋子检测与识别
- 🧠 AI策略决策过程
- 🤖 机械臂精确落子
- 🔄 防悔棋机制演示

> 📥 **下载说明**：点击上方按钮访问Release页面，在Assets部分下载演示视频文件

---

## 📖 项目简介

本项目是针对2024年全国大学生电子设计竞赛E题开发的**高鲁棒性三子棋AI视觉检测系统**。系统集成了计算机视觉、人工智能决策算法和串口通信技术，实现了对三子棋游戏的全自动视觉识别、智能决策和机械臂控制。

### 🎯 核心特性

- **🔍 高精度视觉检测**：基于OpenCV的圆形检测算法，支持黑白棋子识别
- **🧠 智能AI决策**：采用Minimax算法实现最优策略决策
- **🔄 防悔棋机制**：实时监测棋子位置变化，防止人为悔棋
- **📡 串口通信**：支持与机械臂的实时数据交互
- **🎮 多模式支持**：先手/后手模式，旋转校准功能
- **💪 高鲁棒性**：适应不同光照条件和棋盘角度

## 🏗️ 系统架构

```
三子棋AI系统
├── 视觉检测模块 (OpenCV)
│   ├── 棋盘识别
│   ├── 棋子检测
│   └── 颜色分类
├── AI决策模块 (Minimax)
│   ├── 游戏状态评估
│   ├── 最优策略计算
│   └── 胜负判断
├── 通信控制模块
│   ├── 串口通信
│   ├── 指令编码
│   └── 机械臂控制
└── 校准辅助模块
    ├── 坐标映射
    ├── 旋转补偿
    └── 位置校准
```

## 📁 项目结构

```
tic-tac-toe-ai/
├── communication.py      # 串口通信模块
├── decision.py          # AI决策引擎（Minimax算法）
├── first.py            # 先手模式主程序
├── second.py           # 后手模式主程序
├── versionfirst.py     # 先手视觉识别模块（防悔棋）
├── versionsecond.py    # 后手视觉识别模块（防悔棋）
├── rotated.py          # 旋转校准辅助工具
├── rotated4.py         # 旋转后四点定位程序
├── first4.py           # 旋转前四点定位程序
├── firstcenter.py      # 中心点优先策略程序
└── README.md           # 项目文档
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.7+
- **操作系统**: Linux (推荐树莓派) / Windows / macOS
- **硬件**: USB摄像头、串口设备（可选）

### 依赖安装

```bash
# 安装核心依赖
pip install opencv-python numpy pyserial

# 或使用requirements.txt（如果提供）
pip install -r requirements.txt
```

### 硬件连接

1. **摄像头设置**：连接USB摄像头到设备
2. **串口配置**：根据平台修改`communication.py`中的串口参数
   ```python
   # 树莓派GPIO串口
   ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
   
   # USB转串口
   # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
   
   # Windows系统
   # ser = serial.Serial('COM1', 9600, timeout=0.5)
   ```

### 运行程序

#### 1. 先手模式（AI先下）
```bash
python first.py
```

#### 2. 后手模式（人类先下）
```bash
python second.py
```

#### 3. 校准模式
```bash
# 查看旋转校准
python rotated.py

# 四点定位校准
python rotated4.py
```

## 🔧 核心算法

### 视觉检测算法

1. **图像预处理**
   - ROI区域提取 (250×200, 175×175)
   - 灰度转换和二值化
   - 自适应阈值处理
   - 形态学操作（腐蚀）

2. **圆形检测**
   ```python
   circles = cv2.HoughCircles(
       eroded, cv2.HOUGH_GRADIENT, 1, 30,
       param1=250, param2=30,
       minRadius=5, maxRadius=40
   )
   ```

3. **颜色识别**
   - 随机采样像素点
   - 黑白像素统计
   - 颜色分类判断

### AI决策算法

采用经典的**Minimax算法**实现最优策略：

```python
def minimax(chess, depth, is_maximizing):
    if winnerdetect(chess, 2):  # AI获胜
        return 1
    if winnerdetect(chess, 1):  # 人类获胜
        return -1
    if full(chess):  # 平局
        return 0
    
    if is_maximizing:
        # AI回合：选择最大值
        best_score = -float('inf')
        for move in available_moves:
            score = minimax(chess, depth + 1, False)
            best_score = max(score, best_score)
        return best_score
    else:
        # 人类回合：选择最小值
        best_score = float('inf')
        for move in available_moves:
            score = minimax(chess, depth + 1, True)
            best_score = min(score, best_score)
        return best_score
```

## 📡 通信协议

### 串口数据格式

```
帧结构: [帧头高][帧头低][数据][帧尾]
帧头: 0xAA 0x55
帧尾: 0x9A
```

### 指令编码

| 指令类型 | 格式 | 说明 |
|---------|------|------|
| 白棋移动 | `1XY` | X=起始位置, Y=目标位置 |
| 黑棋移动 | `2XY` | X=起始位置, Y=目标位置 |
| 悔棋检测 | `3XY` | X=原位置, Y=新位置 |
| 旋转校准 | `4XY` | 旋转后坐标映射 |
| 特殊指令 | `5XY` | 扩展功能 |

## 🎮 使用说明

### 棋盘坐标系统

```
 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8
```

### 详细使用案例

#### 案例1：先手模式完整对局

```bash
# 1. 启动先手模式
python first.py

# 2. 系统输出
. . .
. . .
. . .

# 3. 将棋盘放在摄像头前，确保在红色框内
# 4. 人类放置第一个白棋子（例如位置4-中心）
# 5. 按Enter键确认
# 系统检测到棋子，输出：
X . .
. . .
. . .

# 6. AI自动计算最优位置并输出指令
# 控制台显示：210
# 串口发送：AA 55 32 31 30 9A

# 7. 继续对局直到游戏结束
```

#### 案例2：后手模式对局

```bash
# 1. 启动后手模式
python second.py

# 2. 输入AI首步位置
first move(0-8): 4

# 3. 系统输出AI首步
. . .
. O .
. . .

# 4. 人类放置棋子，系统自动检测和响应
```

#### 案例3：旋转校准流程

```bash
# 1. 启动校准程序
python rotated.py

# 2. 观察红色校准线是否与棋盘对齐
# 3. 如需调整，运行四点校准
python rotated4.py

# 4. 按提示输入校准参数
global: 1  # 启用旋转映射
enter white1first: 2
enter white1last: 0
# ... 继续输入其他参数

# 5. 按Enter确认每个校准点
```

#### 案例4：防悔棋检测

```bash
# 游戏进行中，如果检测到已放置棋子位置改变：
# 控制台输出：334  # 3=悔棋指令，3=原位置，4=新位置
# 串口发送：AA 55 33 33 34 9A
# 系统自动恢复棋盘状态
```

### 操作流程

1. **环境准备**
   - 确保摄像头正常工作
   - 检查串口连接（如使用机械臂）
   - 准备黑白棋子和棋盘

2. **系统校准**
   - 运行 `rotated.py` 检查视觉校准
   - 如有偏差，使用 `rotated4.py` 进行四点校准
   - 调整摄像头角度和距离

3. **开始游戏**
   - 选择先手模式 (`first.py`) 或后手模式 (`second.py`)
   - 将棋盘放置在红色检测框内
   - 按Enter键开始每轮检测

4. **游戏进行**
   - 人类放置棋子后按Enter确认
   - 系统自动检测棋子位置和颜色
   - AI计算最优策略并输出指令
   - 机械臂执行移动（如已连接）

5. **异常处理**
   - 悔棋检测：自动识别并报警
   - 检测失败：重新调整棋子位置
   - 光照问题：调整环境光线或参数

### 防悔棋机制

系统实时监测已放置棋子的位置变化：
- **检测原理**：比较前后帧中棋子位置
- **触发条件**：已识别棋子坐标发生变化
- **响应动作**：
  - 立即输出悔棋警告
  - 发送悔棋指令 `3XY` (X=原位置, Y=新位置)
  - 恢复游戏状态到合法位置
  - 要求重新放置棋子

## 🔬 技术特点

### 高鲁棒性设计

1. **光照适应性**
   - OTSU自适应阈值
   - 高斯自适应阈值
   - 多重阈值处理

2. **角度容错性**
   - 坐标映射算法
   - 旋转补偿机制
   - 四点校准系统

3. **干扰抑制**
   - ROI区域限制
   - 圆形参数约束
   - 随机采样验证

### 性能优化

- **实时处理**：优化的图像处理流水线
- **内存管理**：及时释放摄像头资源
- **算法效率**：Minimax剪枝优化

## 🛠️ 自定义配置

### 摄像头参数调整

```python
# 分辨率设置
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ROI区域调整
roi_x, roi_y, roi_w, roi_h = 250, 200, 175, 175
```

### 检测参数优化

```python
# 圆形检测参数
circles = cv2.HoughCircles(
    eroded, cv2.HOUGH_GRADIENT, 1, 30,
    param1=250,    # 边缘检测阈值
    param2=30,     # 圆心检测阈值
    minRadius=5,   # 最小半径
    maxRadius=40   # 最大半径
)
```

## 🏆 竞赛优势

- ✅ **完整解决方案**：涵盖视觉、AI、通信全链路
- ✅ **高精度识别**：适应复杂光照和角度条件
- ✅ **智能决策**：Minimax算法保证最优策略
- ✅ **实时性能**：满足竞赛时间要求
- ✅ **鲁棒性强**：多重容错和异常处理
- ✅ **易于部署**：支持多平台运行

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢全国大学生电子设计竞赛组委会
- 感谢OpenCV开源社区
- 感谢所有贡献者和使用者

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: caiths@icloud.com
- 🐛 Issues: [GitHub Issues](https://github.com/poboll/tic-tac-toe-ai/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/poboll/tic-tac-toe-ai/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！