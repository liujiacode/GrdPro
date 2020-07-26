#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from Libs.read_grd import read_grd
import numpy
import sys
import getopt

__str__ = """
名称    : DMol3 density.grd 文件层叠工具.

原理    : 将密度数据导入为三维向量数组array[z, y, x];
          定义平行于z轴的层叠向量(abs_z_from, abs_z_to);
          以切片向量为基础建立垂直于z轴的切面,并以step步长划分近似积分区域,
          得到step_num + 1组积分值数组;
          函数返回(文件信息, 切片向量, 积分步长, 积分步数, 积分值数组)

注意    : 1) 请沿晶格a, b, c方向建立坐标系(可能不是直角坐标系),并使用此坐标建立切片向量;
          2) 选取切片向量时请注意使from值小于to值;
          3) 请谨慎使用格点步长大于1的计算数据.

使用方法: clip -i <density.grd> -f <from point> -t <to point> [-o <result file>, -h]

参数    : (1) -h / --help
             查看命令帮助.
          (2) -i / --input <density.grd>
             导入数据. 后接导入包含数据文本的"绝对路径".
          (3) -o / --output <result file>
             导出结果. 后接导出包含结果文本的"绝对路径".
          (4) -v / --vector <z vector>
             层叠向量(向量须平行于z轴). 后接"from,to"(无括号和空格,即"-v from,to"或"--vector from,to").

"""


def stack(data_file, abs_z_from, abs_z_to):
    if not os.path.isfile(data_file):
        raise ValueError("Invalid data file path.")

    category, lattice_constants, step_args, grd_data = read_grd(data_file)
    a, b, c, alpha, beta, gamma = lattice_constants
    step, i_from, i_to, j_from, j_to, k_from, k_to = step_args
    reshape_size = ((k_to - k_from) // step + 1, (j_to - j_from) // step + 1, (i_to - i_from) // step + 1)
    data_array = numpy.reshape(numpy.array(grd_data), reshape_size)

    if not (isinstance(abs_z_from, int) or isinstance(abs_z_from, float)) or not (isinstance(abs_z_to, int) or isinstance(abs_z_to, float)):
        raise ValueError("Invalid value.")

    z_from = abs_z_from * 1.0 / c * (k_to - k_from)
    z_to = abs_z_to * 1.0 / c * (k_to - k_from)

    z_from = int(z_from // step * step)
    z_to = int(z_to // step * step)

    if z_from < k_from or k_from > k_to:
        raise ValueError("Invalid range of z_from value.")
    if z_to < k_from or z_to > k_to:
        raise ValueError("Invalid range of z_to value.")

    step_num = (z_to - z_from) // step

    profit_data = []
    for i in range(step_num + 1):
        print(data_array[int(z_from + step * i) // step, :, :])
        profit_data.append(sum(sum(data_array[int(z_from + step * i) // step, :, :])))

    data_info = (category, lattice_constants, step_args)
    clip_vector = (z_from, z_to)
    clip_step_length = step
    clip_step_num = step_num + 1

    return data_info, clip_vector, clip_step_length, clip_step_num, profit_data


if __name__ == '__main__':
    opt_args = getopt.getopt(sys.argv[1:], "hi:o:v:", ["help", "input=", "output=", "vector="])[0]
    input_file = ""
    output_file = ""
    z_vector = ()
    for opt, arg in opt_args:
        if opt in ("-h", "--help"):
            print(__str__)
            exit(0)
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-v", "--vector"):
            z_vector = tuple(float(i) for i in arg.split(','))
        else:
            raise ValueError("Invalid opt.")

    if not os.path.isfile(input_file):
        raise ValueError("Invalid input file.")

    data_result = stack(input_file, z_vector[0], z_vector[1])
    context = "Category : " + str(data_result[0][0])
    context += "\nLattice constants : \n    a = {:0}, b = {:1}, c = {:2}, alpha = {:3}, beta = {:4}, gamma = {:5}".format(
        *data_result[0][1])
    context += "\nGrid : \n    interval = {:0}, x_from_to = {:1} -> {:2}, y_from_to = {:3} -> {:4}, z_from_to = {:5} -> {:6}, ".format(
        *data_result[0][2])
    context += "\nClip vector : {0}".format(data_result[1])
    context += "\nClip interval : {0}".format(data_result[2])
    context += "\nTotal : {0}".format(data_result[3])
    context += "\nResult array : \n"
    for result_digit in data_result[4]:
        context += str(result_digit)
        context += '\n'

    if output_file:
        with open(output_file, 'w') as f:
            f.write(context)
    else:
        print(context)
