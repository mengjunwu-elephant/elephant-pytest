from openpyxl import load_workbook


def get_test_data_from_excel(file, sheet_name):
    """
    获取Excel文件中的用例数据
    :param file:
    :param sheet_name:
    :return:
    """
    # 打开Excel
    wb = load_workbook(file, read_only=True)
    # 获取sheet
    sh = wb[sheet_name]
    row = sh.max_row
    column = sh.max_column
    # 获取数据
    data = []
    # 获取第一行的所有key
    keys = []
    for i in range(1, column + 1):
        keys.append(sh.cell(1, i).value)
    # 循环每一行的值，组成字典
    for i in range(2, row + 1):
        temp = {}
        for j in range(1, column + 1):
            # key = keys[j-1]
            # value = sh.cell(i,j).value
            # temp[key] = value
            temp[keys[j - 1]] = sh.cell(i, j).value
        data.append(temp)
    return data


if __name__ == '__main__':
    get_test_data_from_excel(r'../test_data/test_mercury.xlsx', 'Sheet1')
