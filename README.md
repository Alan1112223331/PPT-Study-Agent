# PPT-Study-Agent - 幻灯片翻译与讲解系统

摆脱水老师，让视觉语言模型（VLM）来教你。

## 项目简介

PPT-Study-Agent是一个基于视觉语言模型(VLM)的幻灯片翻译与讲解系统，能够自动分析PPT、PPTX或PDF格式的幻灯片文件，提供中文翻译和详细的知识点讲解。系统特别适合用于：

- 外语幻灯片的中文翻译
- 学术报告和课件的知识点解析
- 技术文档的详细讲解
- 会议材料的快速理解

## 功能特点

- **多格式支持**：支持PPT、PPTX和PDF格式文件
- **实时处理**：上传后即时处理，可实时查看分析进度和结果
- **智能分析**：基于先进的视觉语言模型，提供专业准确的内容分析
- **上下文理解**：分析时保持幻灯片间的上下文连贯性
- **中文输出**：所有分析结果均以中文呈现，便于理解
- **美观界面**：简洁直观的用户界面，操作便捷

## 技术架构

- **前端**：HTML、CSS、JavaScript
- **后端**：Flask (Python)
- **文件处理**：
  - LibreOffice (PPT/PPTX转PDF)
  - pdf2image (PDF转图片)
- **AI模型**：基于OPENAI格式的VLM模型

## 安装步骤

### 前提条件

- Python 3.8+
- LibreOffice (用于PPT/PPTX转换)
- OPENAI格式的API密钥

### 安装过程

1. 克隆仓库

```bash
git clone [仓库地址]
cd pptstudy
```

2. 安装依赖

```bash
# 使用pip安装所有依赖
pip install -r requirements.txt

# 或者使用conda创建新环境并安装依赖
conda create -n pptstudy python=3.8
conda activate pptstudy
pip install -r requirements.txt
```

3. 安装系统依赖

#### Ubuntu/Debian系统

```bash
# 安装LibreOffice和pdf2image所需依赖
sudo apt-get update
sudo apt-get install -y libreoffice poppler-utils

# 安装基本字体
sudo apt-get install -y fonts-liberation fonts-dejavu fontconfig libfontconfig1

# 更新字体缓存
sudo fc-cache -f -v
```

4. 设置环境变量

```bash
# Linux/macOS系统
export XAI_API_KEY=your_api_key_here

# 或者创建.env文件
echo "XAI_API_KEY=your_api_key_here" > .env
```

## 使用方法

1. 启动应用

```bash
python3 app.py
```

2. 在浏览器中访问 `http://localhost:5000`

3. 上传PPT、PPTX或PDF文件

4. 等待处理完成，实时查看分析结果

## 项目结构

```
pptstudy/
├── app.py              # 主应用入口
├── utils/
│   ├── converter.py    # 文件格式转换工具
│   └── analyzer.py     # 图像分析和描述生成
├── static/
│   ├── css/            # 样式文件
│   └── js/             # JavaScript文件
├── templates/          # HTML模板
├── uploads/            # 上传文件存储目录
└── results/            # 处理结果存储目录
```

## 工作流程

1. 用户上传PPT、PPTX或PDF文件
2. 系统将文件转换为PDF格式(如果不是PDF)
3. PDF文件被转换为一系列图像
4. 视觉语言模型分析每张图像并生成描述
5. 用户可以实时查看处理进度和结果

## 注意事项

- 处理大型文件可能需要较长时间
- 确保系统有足够的存储空间用于临时文件
- API调用可能会产生费用，请注意控制使用量

## 常见问题

**Q: 为什么我的PPT文件无法正确转换？**

A: 请确保已正确安装LibreOffice，并且PPT文件格式正确。某些特殊格式或包含特殊元素的PPT可能无法完全支持。

**Q: 分析结果不够准确怎么办？**

A: 分析结果的准确性取决于幻灯片的清晰度和内容复杂度。对于文字较多、结构清晰的幻灯片，分析效果更佳。

**Q: 如何提高处理速度？**

A: 可以尝试减小文件大小，或者调整代码中的DPI参数以生成较小的图像。

## TODO list

- [ ] 完成公式显示的支持
- [ ] 优化文件保存系统
- [ ] 添加多用户管理系统

## License

本项目采用MIT许可证，详细请参考LICENSE文件。