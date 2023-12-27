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
import re

def extract_str_num(excel_path, save_excel_path):
    xls = pd.ExcelFile(excel_path)
    with pd.ExcelWriter(save_excel_path) as writer:
        for name in tqdm(xls.sheet_names):
            neuron = pd.ExcelFile.parse(xls, sheet_name=name)
            mito_trunk = np.array(neuron.iloc[:, 11])
            mito_trunk_new = []
            for i in range(len(mito_trunk)):
                number = re.findall("\d+", mito_trunk[i])
                mito_trunk_new += number
            new_data = pd.DataFrame(mito_trunk_new)
            new_data.columns = ["Trunk_node_num"]
            new_data.to_excel(writer, sheet_name=name, index=False, header=1)
            # print("1")

def statistics(excel_path, excel_path_2, save_excel_path):
    xls_num = pd.ExcelFile(excel_path)
    xls_2 = pd.ExcelFile(excel_path_2)
    with pd.ExcelWriter(save_excel_path) as writer:
        data = pd.ExcelFile.parse(xls_2, sheet_name="jy_new")
        """
        neuron_name_list = data.iloc[:, 0]
        neuron_name, count = np.unique(neuron_name_list, return_counts=True)
        neuron_name_count = {}
        for i, name in enumerate(list(neuron_name)):
            neuron_name_count.update({name: count[i]})
        """
        new_data = []
        for i in range(len(data)):
            neuron_name = data.iloc[i, 0]
            trunk_id = data.iloc[i, 5]
            data_2 = pd.ExcelFile.parse(xls_num, sheet_name=neuron_name)
            mito_num = list(data_2.iloc[:, 0])
            count_mito = mito_num.count(trunk_id)
            new_data.append(list(data.iloc[i, :]) + [count_mito])
        new_data = pd.DataFrame(new_data)
        new_data.columns = ['name', 'id', '#SGN', 'IHC type', 'ribbon type', 'trunk', 'num_mito', 'num_efferent', 'length(um)', "num_mito_unit"]
        new_data.to_excel(writer, sheet_name="jy_new", index=False, header=1)



def excel_sheet_merge(excel_1, excel_2):  # 2 --> 1
    xls = pd.ExcelFile(excel_2)
    with pd.ExcelWriter(excel_1, mode='a', engine='openpyxl',if_sheet_exists='new') as writer:
        for name in tqdm(xls.sheet_names):
            neuron = pd.ExcelFile.parse(xls, sheet_name=name)
            neuron.to_excel(writer, sheet_name=name, index=False, header=1)

def compute_effrent_range_mito_num(excel_path, save_excel_path, W):
    xls = pd.ExcelFile(excel_path)
    with pd.ExcelWriter(save_excel_path) as writer:
        for name in tqdm(xls.sheet_names):
            data = pd.ExcelFile.parse(xls, sheet_name=name)
            neuron_name_list = np.unique(data.iloc[:, 0])
            # for i in range(len(data)):
            node_dict = {}
            for neuron_name in tqdm(list(neuron_name_list)):
                # neuron_name = data.iloc[i, 0]
                data_neuron = data[data["name"] == neuron_name]
                poistion_index = list(data_neuron.index)
                L = len(data_neuron)
                # length_neuron = data_neuron["length(um)"]
                # data_neuron_effernt = data_neuron[data_neuron["num_efferent"] != 0]
                for i in range(L):
                    # data_node_effrent = data_neuron.iloc[i, 7]
                    data_node_length = data_neuron.iloc[i, 8]
                    data_new = data_neuron[(data_neuron["length(um)"] > data_node_length - W/2) & (data_neuron["length(um)"] < data_node_length + W/2)]
                    if data_new["num_efferent"].sum() != 0:
                        node_dict.update({poistion_index[i]: 1})
                    else:
                        node_dict.update({poistion_index[i]: 0})
            node_efferent = []
            for key in sorted(node_dict):
                node_efferent.append(node_dict[key])
            data['efferent_or_not'] = node_efferent
            data.to_excel(writer, sheet_name=name, index=False, header=1)
            # print("1")

def terminal_mito(excel_path_1, excel_path_2, save_excel_path):
    xls_1 = pd.ExcelFile(excel_path_1)
    xls_2 = pd.ExcelFile(excel_path_2)
    data_2 = pd.ExcelFile.parse(xls_2, sheet_name="jy_new")
    data_total = pd.DataFrame()
    data_name_terminal = []
    with pd.ExcelWriter(save_excel_path) as writer:
        for name in tqdm(xls_1.sheet_names):
            data_1 = pd.ExcelFile.parse(xls_1, sheet_name=name)
            # 找到terminal的节点
            data_neuron = data_2[data_2["name"] == name]
            value_90 = max(list(data_neuron["length(um)"])) * 0.9
            data_neuron_90 = data_neuron[data_neuron["length(um)"] >= value_90]
            node_90 = list(data_neuron_90["trunk"])
            node_90_str = [str(i).zfill(2) for i in node_90]
            #
            mito_index = len(data_1)
            mito_terminal = []

            for i in range(mito_index):
                node = data_1.iloc[i, 11]
                num_list = re.findall("\d+", node)
                L_num = len(num_list)
                count = 0
                flag = 0
                for unit_node in num_list:
                    if unit_node in node_90_str:
                        count += 1
                if count >= L_num/2:
                    flag = 1
                mito_terminal.append(flag)

            N_terminal = sum(mito_terminal)
            data_name_terminal.append([name, N_terminal])

            data_1["mito_terminal"] = mito_terminal
            data_terminal_1 = data_1[data_1["mito_terminal"] == 1]
            L = len(data_terminal_1)
            if L > 0:
                value_name = [name] * L
                data_terminal_1.insert(loc=0, column='name', value=value_name)
                data_total = pd.concat([data_total, data_terminal_1])
        data_total.to_excel(writer, sheet_name="mito_terminal_1", index=False, header=1)

        data_name_terminal = pd.DataFrame(data_name_terminal)
        data_name_terminal.columns = ["name", "N_mito_terminal"]
        data_name_terminal.to_excel(writer, sheet_name="N_mito_terminal", index=False, header=1)
            # data_1.to_excel(writer, sheet_name=name, index=False, header=1)

if __name__ == "__main__":
    """
    excel_path = r"E:\jiangy\dataset\CBA\HuaLab-CBA-wt-base-002\mito_proof\mito_assign_trunk_02_new.xlsx"
    save_excel_path = r"E:\jiangy\dataset\CBA\HuaLab-CBA-wt-base-002\mito_proof\mito_assign_trunk_02_new_num.xlsx"
    extract_str_num(excel_path, save_excel_path)
    """
    """
    # statistics
    excel_path = r"E:\jiangy\dataset\CBA\mito_assign_trunk_01_02_new_num_merge.xlsx"
    excel_path_2 = r"E:\jiangy\dataset\CBA\SGN.xlsx"
    save_excel_path = r"E:\jiangy\dataset\CBA\SGN_mito_num.xlsx"
    statistics(excel_path, excel_path_2, save_excel_path)
    """
    """
    # excel_2 merge to excel_1
    excel_1 = r"E:\jiangy\dataset\CBA\mito_assign_trunk_01_new.xlsx"
    excel_2 = r"E:\jiangy\dataset\CBA\mito_assign_trunk_02_new.xlsx"
    excel_sheet_merge(excel_1, excel_2)
    """

    """
    excel_path = r"E:\jiangy\dataset\CBA\SGN_mito_num.xlsx"
    save_excel_path = r"E:\jiangy\dataset\CBA\SGN_mito_num_new.xlsx"
    W = 5  # range 5um
    compute_effrent_range_mito_num(excel_path, save_excel_path, W)
    """

    excel_path_1 = r"E:\jiangy\dataset\CBA\mito_assign_trunk_01_02_new_merge.xlsx"
    excel_path_2 = r"E:\jiangy\dataset\CBA\SGN_mito_num_new.xlsx"
    # save_excel_path = r"E:\jiangy\dataset\CBA\SGN_mito_num_new_new_1.xlsx"
    save_excel_path = r"E:\jiangy\dataset\CBA\SGN_mito_num_new_new_2.xlsx"
    terminal_mito(excel_path_1, excel_path_2, save_excel_path)


