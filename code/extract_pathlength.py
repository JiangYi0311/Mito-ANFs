from itertools import combinations
from typing import Iterator, Tuple
import numpy as np
from scipy.spatial import cKDTree
import webknossos as wk
import pandas as pd
import os
from PIL import Image
from tqdm import tqdm
from skimage import io

def calculate_distance_3d(a, b, Pixel):
    dist = np.zeros((a.shape[0], b.shape[0]))
    for i in tqdm(range(a.shape[0])):
        dist[i, :] = (np.sum(((b - a[i, :]) * Pixel) ** 2, axis=1)) ** 0.5
    return dist

def serial_to_stack(path):
    filename = sorted(os.listdir(path))
    N = len(filename)
    img = Image.open(os.path.join(path, filename[0]))
    W, H = img.size
    print('******* Create an empty image_stack *******')
    stack = np.empty((N, H, W), np.uint16)
    print('******* Read image *******')
    for i, name in tqdm(enumerate(filename)):
        stack[i, :, :] = io.imread(os.path.join(path, name))
    return stack

def mito_assign_skeleton(image_path, excel_path, trunk_node_path, save_excel_path, Pixel, left_position):

    image_stack = serial_to_stack(image_path)  # 3D data
    v_per = 0.07 * 1000 * 1000 * 1000  # nm^3
    xls = pd.ExcelFile(excel_path)
    trunk_node_xls = pd.ExcelFile(trunk_node_path)
    # w_0, h_0, z_0 = left_position[0], left_position[1], left_position[2]
    with pd.ExcelWriter(save_excel_path) as writer:
        for name in tqdm(xls.sheet_names):
            data = pd.ExcelFile.parse(xls, sheet_name=name)
            trunk_node = pd.ExcelFile.parse(trunk_node_xls, sheet_name=name)
            coord_trunk = np.array(trunk_node.iloc[:, :3])  # 主干节点坐标
            L = len(data)
            new_data = []
            for i in range(L):
                #  获取线粒体的中点
                id_mito = int(data.iloc[i, 3].split('-')[1])  # 线粒体id

                v_mito_time = int(data.iloc[i, 5] / v_per) + 1  # 线粒体体积是0.07um^3的倍数
                coord = np.where(image_stack == id_mito)
                coord = np.array(coord).T  # z, x, y

                if v_mito_time == 1:
                    central_mito = [np.median(coord[:, 0]), np.median(coord[:, 1]), np.median(coord[:, 2])]
                    central_mito = np.array(central_mito)  # image coord
                    central_mito = central_mito + np.array(left_position)  # webknossos coord
                    central_mito = central_mito[::-1]  # 一维数组反转
                    central_mito = central_mito.reshape(1, -1)

                    # print("compute distance")
                    dist = calculate_distance_3d(central_mito, coord_trunk, Pixel)
                    # dist = np.min(dist, axis=1)  # 最小值
                    index_node = np.argmin(dist)  # 最短距离对应的索引
                    mito_trunk = trunk_node.iloc[index_node, 3]
                    new_data.append(list(data.iloc[i, :]) + [mito_trunk])
                else:
                    # print(v_mito_time, i)
                    d_v = np.ptp(coord*np.array([50, 12, 12]), axis=0)  # difference_value resolution
                    d_v_0 = np.ptp(coord, axis=0)  # difference_value
                    maxindex = np.argmax(d_v)  # 哪个维度上跨度最大
                    list_mito = []
                    # coord_max = np.max(coord, axis=0)
                    coord_min = np.min(coord, axis=0)
                    d_v_per = d_v_0 / v_mito_time
                    for k in range(1, v_mito_time+1):
                        coord_temp = coord[coord[:, maxindex] <= (coord_min[maxindex] + d_v_per[maxindex])]
                        coord_final = coord_temp[coord_temp[:, maxindex] > (coord_min[maxindex] + (k-1) * d_v_per[maxindex])]

                        central_mito = [np.median(coord_final[:, 0]), np.median(coord_final[:, 1]), np.median(coord_final[:, 2])]
                        central_mito = np.array(central_mito)  # image coord
                        central_mito = central_mito + np.array(left_position)  # webknossos coord
                        central_mito = central_mito[::-1]  # 一维数组反转
                        central_mito = central_mito.reshape(1, -1)

                        # print("compute distance")
                        dist = calculate_distance_3d(central_mito, coord_trunk, Pixel)
                        # dist = np.min(dist, axis=1)  # 最小值
                        index_node = np.argmin(dist)  # 最短距离对应的索引
                        mito_trunk = trunk_node.iloc[index_node, 3]
                        list_mito.append(mito_trunk)
                    new_data.append(list(data.iloc[i, :]) + [list_mito])

            new_data = pd.DataFrame(new_data)
            new_data.columns = ["X", "Y", "Z", "Comment", "Volume", "volume(nm^3)", "Shape_VA3d", "Length3d(nm)", "Thickness3d(nm)", "Area3d(nm^2)", "MCI", "Trunk_node"]
            new_data.to_excel(writer, sheet_name=name, index=False, header=1)


if __name__ == "__main__":
    image_path = r"E:\jiangy\dataset\CBA\HuaLab-base-CBA-wt\mito_proof\mito_0_890_proof"
    excel_path = r"E:\jiangy\dataset\CBA\HuaLab-base-CBA-wt\mito_proof\position_comment_modify_01_volume+amira+MCI.xlsx"
    trunk_node_path = r"E:\jiangy\dataset\CBA\HuaLab-base-CBA-wt\mito_proof\trunk_node.xlsx"
    save_excel_path = r"E:\jiangy\dataset\CBA\HuaLab-base-CBA-wt\mito_proof\mito_assign_trunk_01_new.xlsx"
    Pixel = [12, 12, 50]
    # w_0, h_0, z_0 = 2100, 5900, 0  # webknossos和下载图像起始点的差异  HuaLab-base-CBA-wt
    # w_0, h_0, z_0 = 4100, 6500, 650  # webknossos和下载图像起始点的差异  HuaLab-CBA-wt-base-002
    left_position = [0, 5900, 2100]  # n, h, w
    mito_assign_skeleton(image_path, excel_path, trunk_node_path, save_excel_path, Pixel, left_position)