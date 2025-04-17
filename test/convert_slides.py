#!/usr/bin/env python3
"""
课件转图片工具 - 将PPT、PPTX和PDF文件转换为图片
适用于Ubuntu服务器环境，解决字体缺失问题
"""

import os
import sys
import argparse
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


def convert_pdf_to_images(pdf_path, output_dir, dpi=150, format='png', batch_size=1):
    """将PDF文件转换为图片，批量处理以减少内存使用"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名（不含扩展名）用于输出文件命名
    file_name = Path(pdf_path).stem
    
    # 转换PDF为图片，使用内存优化选项
    image_paths = []
    
    try:
        # 首先获取PDF页数
        info = subprocess.check_output(['pdfinfo', pdf_path]).decode()
        pages = 0
        for line in info.split('\n'):
            if 'Pages:' in line:
                pages = int(line.split(':')[1].strip())
                break
        
        # 批量处理页面
        for i in range(0, pages, batch_size):
            end_page = min(i + batch_size, pages)
            print(f"处理页面 {i+1} 到 {end_page}，共 {pages} 页...")
            
            # 使用内存优化参数
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=i+1,
                last_page=end_page,
                use_pdftocairo=True,  # 使用pdftocairo通常更节省内存
                thread_count=1        # 减少线程数
            )
            
            # 保存这批图片
            for j, image in enumerate(images):
                page_num = i + j + 1
                output_file = os.path.join(output_dir, f"{file_name}_page_{page_num}.{format}")
                image.save(output_file, format.upper())
                image_paths.append(output_file)
                
                # 手动释放内存
                del image
        
        return image_paths
    except Exception as e:
        print(f"PDF转图片出错: {e}")
        return []


def convert_ppt_to_pdf_direct(ppt_path, output_dir):
    """使用LibreOffice直接将PPT/PPTX转换为PDF"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名（不含扩展名）用于输出文件命名
    file_name = Path(ppt_path).stem
    output_pdf = os.path.join(output_dir, f"{file_name}.pdf")
    
    # 使用LibreOffice转换PPT/PPTX为PDF
    cmd = [
        'soffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        ppt_path
    ]
    
    try:
        print("正在使用LibreOffice转换PPT/PPTX为PDF...")
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        
        # 检查是否成功生成PDF
        if os.path.exists(output_pdf):
            print(f"成功生成PDF: {output_pdf}")
            return output_pdf
        else:
            print(f"转换失败：无法找到输出的PDF文件")
            return None
    except subprocess.CalledProcessError as e:
        print(f"转换PPT为PDF时出错: {e}")
        return None


def convert_ppt_with_inkscape(ppt_path, output_dir):
    """使用inkscape作为中介转换PPT/PPTX文件"""
    try:
        # 检查是否安装了inkscape
        subprocess.run(['inkscape', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("尝试安装inkscape...")
        try:
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'inkscape'], check=True)
        except Exception as e:
            print(f"安装inkscape失败: {e}")
            return None
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名（不含扩展名）用于输出文件命名
    file_name = Path(ppt_path).stem
    
    # 先转换为SVG
    temp_dir = tempfile.mkdtemp()
    svg_dir = os.path.join(temp_dir, "svg")
    os.makedirs(svg_dir, exist_ok=True)
    
    try:
        # 使用LibreOffice转换为SVG
        cmd1 = [
            'soffice',
            '--headless',
            '--convert-to', 'svg',
            '--outdir', svg_dir,
            ppt_path
        ]
        subprocess.run(cmd1, check=True)
        
        # 获取所有生成的SVG文件
        svg_files = [os.path.join(svg_dir, f) for f in os.listdir(svg_dir) if f.endswith('.svg')]
        
        # 使用inkscape将SVG转换为PDF
        output_pdf = os.path.join(output_dir, f"{file_name}.pdf")
        if svg_files:
            cmd2 = ['inkscape', '--export-filename=' + output_pdf]
            cmd2.extend(svg_files)
            subprocess.run(cmd2, check=True)
            
            if os.path.exists(output_pdf):
                return output_pdf
    except Exception as e:
        print(f"使用inkscape转换失败: {e}")
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return None


def convert_ppt_with_unoconv(ppt_path, output_dir):
    """使用unoconv转换PPT/PPTX文件"""
    try:
        # 检查是否安装了unoconv
        subprocess.run(['unoconv', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("尝试安装unoconv...")
        try:
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'unoconv'], check=True)
        except Exception as e:
            print(f"安装unoconv失败: {e}")
            return None
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名（不含扩展名）用于输出文件命名
    file_name = Path(ppt_path).stem
    output_pdf = os.path.join(output_dir, f"{file_name}.pdf")
    
    try:
        # 使用unoconv转换为PDF
        cmd = ['unoconv', '-f', 'pdf', '-o', output_pdf, ppt_path]
        subprocess.run(cmd, check=True)
        
        if os.path.exists(output_pdf):
            return output_pdf
    except Exception as e:
        print(f"使用unoconv转换失败: {e}")
    
    return None


def convert_ppt_to_pdf(ppt_path, output_dir):
    """尝试多种方法将PPT/PPTX转换为PDF"""
    # 方法1: 直接使用LibreOffice转换
    pdf_path = convert_ppt_to_pdf_direct(ppt_path, output_dir)
    if pdf_path:
        return pdf_path
    
    print("直接转换失败，尝试安装基本字体...")
    install_basic_fonts()
    
    # 再次尝试直接转换
    pdf_path = convert_ppt_to_pdf_direct(ppt_path, output_dir)
    if pdf_path:
        return pdf_path
    
    # 方法2: 使用unoconv
    print("尝试使用unoconv转换...")
    pdf_path = convert_ppt_with_unoconv(ppt_path, output_dir)
    if pdf_path:
        return pdf_path
    
    # 方法3: 使用inkscape
    print("尝试使用inkscape转换...")
    pdf_path = convert_ppt_with_inkscape(ppt_path, output_dir)
    if pdf_path:
        return pdf_path
    
    print("所有转换方法均失败")
    return None


def convert_presentation_to_images(input_file, output_dir, dpi=150, format='png', batch_size=1):
    """将演示文稿（PPT、PPTX或PDF）转换为图片"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查文件类型
    file_ext = Path(input_file).suffix.lower()
    
    if file_ext in ['.pdf']:
        # 直接转换PDF为图片
        return convert_pdf_to_images(input_file, output_dir, dpi, format, batch_size)
    
    elif file_ext in ['.ppt', '.pptx']:
        # 先将PPT/PPTX转换为PDF，再转换为图片
        pdf_path = convert_ppt_to_pdf(input_file, output_dir)
        if pdf_path:
            return convert_pdf_to_images(pdf_path, output_dir, dpi, format, batch_size)
        else:
            return []
    
    else:
        print(f"不支持的文件类型: {file_ext}")
        return []


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将课件(PPT, PPTX, PDF)转换为图片')
    parser.add_argument('input_file', help='输入文件路径(PPT, PPTX, PDF)')
    parser.add_argument('-o', '--output-dir', default='output', help='输出目录路径')
    parser.add_argument('-d', '--dpi', type=int, default=150, help='图片DPI分辨率 (默认150，越低内存占用越小)')
    parser.add_argument('-f', '--format', default='png', choices=['png', 'jpg', 'jpeg', 'tiff'], 
                        help='输出图片格式')
    parser.add_argument('-b', '--batch-size', type=int, default=1, help='每批处理的页数 (默认1，减少内存使用)')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.isfile(args.input_file):
        print(f"错误: 输入文件 '{args.input_file}' 不存在")
        sys.exit(1)
    
    # 执行转换
    image_paths = convert_presentation_to_images(
        args.input_file, 
        args.output_dir,
        args.dpi,
        args.format,
        args.batch_size
    )
    
    # 输出结果
    if image_paths:
        print(f"成功转换 {len(image_paths)} 页到 {args.output_dir} 目录")
        for path in image_paths:
            print(f"  - {path}")
    else:
        print("转换失败")


if __name__ == "__main__":
    main()
