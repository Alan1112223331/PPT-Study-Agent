import os
import json
import base64
from openai import OpenAI
import mimetypes

mimetypes.add_type('image/png', '.png')
mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx')
mimetypes.add_type('application/vnd.ms-powerpoint', '.ppt')
mimetypes.add_type('application/pdf', '.pdf')

# 从环境变量读取API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("环境变量 OPENAI_API_KEY 未设置")

# 初始化API客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://axa.alan-m-12.top/api",
)

def encode_image(image_path):
    """将图像编码为base64字符串"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def analyze_image(image_path, context=None):
    """分析单张图像并生成描述"""
    base64_image = encode_image(image_path)
    
    # 准备提示文本
    prompt = """
# PPT 幻灯片内容分析助手 (学生友好版)

**任务：** 请按照以下步骤和要求，分析提供的 PPT 幻灯片内容，生成一份结构清晰、易于学生理解和学习的分析报告。

**第一步：判断幻灯片类型**

*   检查幻灯片是否为封面页、纯标题页、目录页或结束页。
*   **如果是** 上述任何一种类型，请直接回复：
    ```
    这张幻灯片属于结构性页面（封面/标题/目录/结束页），主要起组织结构作用，无需进行详细内容分析。
    ```
*   **如果不是** 上述类型，请继续执行第二步。

**第二步：详细内容分析（仅针对非结构性页面）**

请严格按照以下顺序和 Markdown 格式输出分析结果：

---

**【幻灯片核心内容翻译】**

*   **检查原文语言：**
    *   如果幻灯片内容**包含任何非中文文本**（如英文、日文、公式符号等），请在此处提供**完整、通顺、准确的中文翻译**。翻译应力求自然流畅，符合中文表达习惯，像一篇完整的段落或列表，而不是逐行生硬对应。**请勿在此部分使用项目符号（点号）进行逐条翻译，也不要在译文中直接括号标注英文。**请对关键词进行**加粗**处理，以便学生阅读。
    *   如果幻灯片原文**完全是中文**，请在此处注明：“幻灯片原文为中文，无需翻译。”

*   **格式要求：** 本部分内容单独成段展示，保持原文的段落或列表结构（如果原文有）。

---

**【关键术语与词汇表】**

*   **提取术语：** 如果进行了翻译，请在此处**列出**幻灯片中出现的**关键专业术语、缩写或重要概念**的中英文对照。
*   **格式要求：**
    *   使用列表格式，每行一个术语。
    *   格式为：`中文术语 (English Term)` 或 `英文术语 (中文翻译)`。
    *   **仅列出术语对照，不加额外解释。**
    *   如果无需翻译或没有明显关键术语，则注明：“无关键术语需要单独列出。”

---

**【核心知识点提炼】**

*   **提取要点：** 简洁、清晰地**分点列出**幻灯片所呈现的核心知识点、主要概念或关键信息。
    *   使用简单的项目符号（例如 `-` 或 `*`）列出，每个要点占一行。
    *   **要点应高度概括，避免细节展开。**
    *   **请勿在本部分使用加粗强调。**
*   **字数限制：** 本部分总字数**建议不超过 100 字**，确保精炼。

---

**【深入解析与拓展学习】**

*   **详细讲解：** 针对【核心知识点提炼】中列出的要点，进行**深入浅出**的专业讲解和背景补充。内容应具有逻辑性，易于学生理解。
    *   **讲解重点（根据幻灯片内容选择相关点）：**
        *   **概念辨析：** 清晰解释关键概念的定义、内涵和外延，可与其他概念对比。
        *   **原理阐释：** 解释公式、模型、算法背后的原理、物理意义或数学基础。
        *   **技术细节：** 补充相关的实现方法、关键参数或步骤。
        *   **应用与意义：** 探讨知识点的实际应用场景、重要性或局限性。
        *   **背景关联：** 提供必要的上下文，如技术发展、所属领域等。
    *   **要求：** 内容需具体、有深度，贴合学科背景，避免空泛描述。**可以使用加粗**来强调**非常关键**的术语或概念定义，但需谨慎使用。
*   **字数限制：** 本部分总字数**建议不超过 400 字**。
*   **格式要求：** 段落清晰，逻辑连贯。

---

**整体输出规范：**

*   **Markdown 格式：** 使用 Markdown 语法（如标题、列表、`*斜体*`、`**加粗**`、代码块等）使报告清晰美观。
* 数学公式规范要求
* 1. 所有数学公式必须使用LaTeX语法
* 2. 行内公式使用$...$包裹
* 3. 块级公式使用$$...$$包裹
* 4. 避免在公式中使用特殊字符，如需使用请转义
* 5. 确保公式语法正确，避免渲染错误
*   **分隔：** 各主要部分（【】标题标识的部分）之间使用 `---` 分隔线，增加视觉区分度。
*   **语言：** 回答语言为**简体中文**。
*   **风格：** 整体风格应简洁、专业，同时**易于学生阅读和理解**。

"""

    # 如果有上下文，添加到提示中
    if context:
        prompt += "\n\n以下是之前幻灯片的分析，请确保分析的连贯性：\n" + context
    
    # 创建消息
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high",
                    },
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        },
    ]
    
    # 调用API
    try:
        completion = client.chat.completions.create(
            model="X.grok-2-vision-1212",
            messages=messages,
            temperature=0.2,
        )
        
        # 返回生成的描述
        return completion.choices[0].message.content
    except Exception as e:
        print(f"调用API出错: {str(e)}")
        return f"分析失败: {str(e)}"

def analyze_images_realtime(image_paths, output_dir, callback=None):
    """分析多张图像并生成描述，同时保持上下文连贯性，支持实时回调"""
    os.makedirs(output_dir, exist_ok=True)
    
    descriptions = []
    context = ""
    
    # 调整图像路径，确保使用统一格式
    sorted_image_paths = sorted([os.path.abspath(p) for p in image_paths])
    
    # 按顺序处理每张图片
    for i, image_path in enumerate(sorted_image_paths):
        print(f"正在分析第 {i+1}/{len(sorted_image_paths)} 张图片: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"警告: 文件不存在: {image_path}")
            continue
        
        # 分析图片，包含上下文
        description = analyze_image(image_path, context)
        descriptions.append(description)
        
        # 保存描述到文件
        output_file = os.path.join(output_dir, f"description_{i+1:03d}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"description": description}, f, ensure_ascii=False, indent=2)
        
        # 更新上下文，只保留最近5张幻灯片的描述
        context_entries = descriptions[-5:] if len(descriptions) > 5 else descriptions
        context = "\n\n".join([f"幻灯片 {j+1}: {desc}" for j, desc in enumerate(context_entries, i-len(context_entries)+1)])
        
        # 调用回调函数通知进度更新
        if callback:
            callback(i, description)
    
    return descriptions
