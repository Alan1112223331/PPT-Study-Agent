import os
import sys
import subprocess
import tempfile
from pathlib import Path
from pdf2image import convert_from_path


def install_basic_fonts():
    """安装基本字体"""
    print("正在安装基本字体...")
    try:
        # 安装最基本的字体包
        subprocess.run([
            'sudo', 'apt-get', 'update'
        ], check=True)

        subprocess.run([
            'sudo', 'apt-get', 'install', '-y',
            'fonts-liberation', 'fonts-dejavu', 'fontconfig', 'libfontconfig1'
        ], check=True)

        # 更新字体缓存
        subprocess.run(['sudo', 'fc-cache', '-f', '-v'], check=True)

        print("基本字体安装完成")
        return True
    except Exception as e:
        print(f"安装字体时出错: {e}")
        return False


def convert_pdf_to_images(pdf_path, output_dir, dpi=150, format='png'):
    """将PDF文件转换为图片"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取文件名（不含扩展名）用于输出文件命名
    file_name = Path(pdf_path).stem

    # 转换PDF为图片
    image_paths = []

    try:
        # 转换所有页面
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            use_pdftocairo=True,
            thread_count=2
        )

        # 保存图片
        for i, image in enumerate(images):
            page_num = i + 1
            output_file = os.path.join(output_dir, f"{file_name}_page_{page_num:03d}.{format}")
            image.save(output_file, format.upper())
            image_paths.append(output_file)

        return image_paths
    except Exception as e:
        print(f"PDF转图片出错: {e}")
        raise


def convert_ppt_to_pdf(ppt_path, output_dir):
    """使用多种方法尝试将PPT/PPTX转换为PDF"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取文件名（不含扩展名）用于输出文件命名
    file_name = Path(ppt_path).stem
    output_pdf = os.path.join(output_dir, f"{file_name}.pdf")

    # 方法1: 直接使用LibreOffice转换
    try:
        print("正在使用LibreOffice转换PPT/PPTX为PDF...")
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            ppt_path
        ]
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)

        if os.path.exists(output_pdf):
            print(f"成功生成PDF: {output_pdf}")
            return output_pdf
    except:
        print("直接转换失败，尝试安装基本字体...")
        install_basic_fonts()

    # 再次尝试直接转换
    try:
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            ppt_path
        ]
        subprocess.run(cmd, check=True)

        if os.path.exists(output_pdf):
            print(f"成功生成PDF: {output_pdf}")
            return output_pdf
    except:
        print("直接转换仍然失败，尝试使用unoconv...")

    # 方法2: 使用unoconv
    try:
        # 检查是否安装了unoconv
        subprocess.run(['unoconv', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("尝试安装unoconv...")
        try:
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'unoconv'], check=True)
        except Exception as e:
            print(f"安装unoconv失败: {e}")
            raise

    try:
        # 使用unoconv转换为PDF
        cmd = ['unoconv', '-f', 'pdf', '-o', output_pdf, ppt_path]
        subprocess.run(cmd, check=True)

        if os.path.exists(output_pdf):
            print(f"使用unoconv成功生成PDF: {output_pdf}")
            return output_pdf
    except Exception as e:
        print(f"使用unoconv转换失败: {e}")
        raise Exception("所有转换方法均失败")


def convert_to_images(input_file, output_dir, dpi=150):
    """将演示文稿（PPT、PPTX或PDF）转换为图片"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 检查文件类型
    file_ext = Path(input_file).suffix.lower()

    if file_ext in ['.pdf']:
        # 直接转换PDF为图片
        return convert_pdf_to_images(input_file, output_dir, dpi)

    elif file_ext in ['.ppt', '.pptx']:
        # 先将PPT/PPTX转换为PDF，再转换为图片
        pdf_path = convert_ppt_to_pdf(input_file, output_dir)
        if pdf_path:
            return convert_pdf_to_images(pdf_path, output_dir, dpi)
        else:
            raise Exception("无法转换PPT为PDF")

    else:
        raise Exception(f"不支持的文件类型: {file_ext}")
