# Mercury-Pytest环境部署

## 1.Java环境部署

1.1 打开终端执行

```
sudo apt install openjdk-8-jdk
```

1.2 验证是否安装成功

```
java -version
```



## 2.allure环境部署

2.1 下载离线allure包

 [allure-2.34.1.tgz](allure-2.34.1.tgz) 

2.2 解压allure压缩包

```
sudo mkdir -p /opt/allure  # 创建目录
sudo tar -zxvf allure-2.34.1.tgz -C /opt/allure  # 注意参数大写-C
```

2.3 配置allure环境变量

```
echo 'export PATH=$PATH:/opt/allure/allure-2.34.1/bin' >> ~/.bashrc
source ~/.bashrc
```

2.4 验证allure是否安装成功

```
allure --version
```

## 3.依赖库安装

3.1打开终端，cd进入elephant-pytest目录下，执行命令

```
pip3 install -r requirements.txt
```
## 4.python环境变量配置
4.1打开终端，运行以下指令
```
export PYTHONPATH="/home/elephant/Desktop/elephant-pytest:$PYTHONPATH"
```

## 5. 测试框架说明（与 mycobot_450 分支对齐）

- **`pytest.ini`**：`pythonpath = .`（减少 `ModuleNotFoundError: common1`）；markers：`hardware` / `slow` / `smoke` / `regression`；`testcases/` 下用例由 **`conftest.py`** 自动打 **`hardware`**（CI 可用 `pytest -m "not hardware"`）。
- **`conftest.py`**：`mercury_left_port`（session）、默认 **`device`**（仅连接与 `close`，**不自动上电**）。各用例文件内的 **`device` fixture 会覆盖** 根配置。
- **`settings.MercuryBase`（Mercury A1 单臂）**：
  - pymycobot 实例字段为 **`self.mc`**（已从 X1 双臂的 `ml`/`mr` 全量改为单实例 `mc`）。
  - 串口：**`MERCURY_PORT`** 或兼容旧名 **`MERCURY_LEFT_PORT`**，默认 **`/dev/ttyAMA1`**（Windows 可设为 `COM3`）。
  - 串口日志：`MERCURY_SAVE_SERIAL_LOG`（默认 `1`）。
  - 等待停止超时：`MERCURY_MOVE_TIMEOUT_SEC`（默认 `120`，`wait()` 未传 `timeout` 时使用）。
- **Excel**：`common1/test_data_handler.get_test_data_from_excel` 支持 `required_columns`、空行跳过、sheet 校验；约定见 **`docs/EXCEL_TEST_DATA.md`**。
