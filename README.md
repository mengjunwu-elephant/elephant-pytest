# Linux-Pytest环境部署

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
pip install -r requirements.txt
```



## **Windows系统Pytest测试框架部署指南**

### **一、环境准备**

1. **Python环境**

   - 确保已安装Python 3.7+版本（推荐3.8+）

   - 验证安装：`python --version`

   - 建议使用虚拟环境（可选）：

     `python -m venv venv .\venv\Scripts\activate `

2. **JDK安装**

   - 下载JDK 1.8+并配置环境变量
   - 验证：`where java`

### **三、Allure报告集成**

1. **验证安装**

   `allure --version `
