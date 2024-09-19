import os
import requests
from web3 import Web3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from solcx import compile_standard, install_solc, set_solc_version
import json

# 设置Etherscan API密钥和合约地址
ETHERSCAN_API_KEY = '2SWP1Y68AUA6ND9GM1BV3PYVWPJ3ZFQRJK'
CONTRACT_ADDRESS = '0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e'
GANACHE_PRIVATE_KEY = '0x3ca00cdcd2433b2cda774027d76a8794c818d41d51b80c6de59d1f137b872109'

# # 设置Ganache网络的URL
# GANACHE_URL = 'http://127.0.0.1:7545'

# # 连接到Ganache网络
# w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# # 检查是否连接成功
# if not w3.is_connected():
#     raise Exception("Failed to connect to Ganache")

# 安装最新版本的solc
# latest_solc_version = '0.8.20'  # 替换为最新的 Solidity 版本号
# install_solc(version=latest_solc_version)
# set_solc_version(latest_solc_version)

# 根据给定的地址和API密钥获取合约的ABI和源码
def get_contract_data(address, api_key):
    url = f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}'
    
    # 创建一个Session对象
    session = requests.Session()
    
    # 设置重试策略
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 429])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    response = session.get(url)
    data_source_code = response.json()
    source_code = data_source_code['result'][0]['SourceCode']
    abi = data_source_code['result'][0]['ABI']
    
    if source_code.startswith('{'):
        # 处理包含多个文件的JSON对象
        source_code = json.loads(source_code[1:-1])
        main_source = None
        for key, value in source_code['sources'].items():
            print(key)
            if key.endswith('.sol'):
                main_source = value['content']
                break
        if main_source is None:
            raise Exception("Main source file not found")
        return main_source, abi
        
    else:
        # 处理单一的Solidity文件
        return source_code, abi

# 对合约源码进行清理，去除注释和空白行
def clean_source_code(source_code):
    single_line_comment_pattern = re.compile(r'//.*')
    multi_line_comment_pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
    blank_line_pattern = re.compile(r'^\s*$', re.MULTILINE)

    cleaned_code = re.sub(multi_line_comment_pattern, '', source_code)
    cleaned_code = re.sub(single_line_comment_pattern, '', cleaned_code)
    cleaned_code = re.sub(blank_line_pattern, '', cleaned_code)

    lines = cleaned_code.splitlines()
    code_lines = [line for line in lines if line.strip()]
    return cleaned_code, len(code_lines)

# 根据给定的交易量最大合约的地址获得其源码和ABI并保存到本地文件
def get_popular_sc():
    with open('./popularSC.json', 'r') as f:
        popular_sc = json.loads(f.read())
    output_folder = 'contracts_output'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder {output_folder}")
    for index, contract in enumerate(popular_sc, start=1):
        print(f"Processing contract {index}/{len(popular_sc)}: {contract['address']}")
        address = contract['address']
        # try:
        source_code, abi = get_contract_data(address, ETHERSCAN_API_KEY)
        print(f"Successfully retrieved contract data for {address}")
        
        cleaned_code, code_lines = clean_source_code(source_code)
        print(f"Cleaned source code for {address} has {code_lines} lines")

        source_file_path = os.path.join(output_folder, f"{address}.sol")
        abi_file_path = os.path.join(output_folder, f"{address}.json")
        
        with open(source_file_path, 'w') as source_file:
            source_file.write(cleaned_code)
        
        with open(abi_file_path, 'w') as abi_file:
            abi_file.write(abi)
        print(f'Successfully saved contract {address} to {source_file_path} and {abi_file_path}')
            
        # except Exception as e:
        #     print(f'Failed to process contract {address}: {e}')

if __name__ == "__main__":
    get_popular_sc()
    