import json
import re
from web3 import Web3
import solcx

# 连接到Ganache
ganache_url = 'http://127.0.0.1:7545'  # 请根据您的Ganache设置调整
web3 = Web3(Web3.HTTPProvider(ganache_url))

# 检查连接
if not web3.is_connected():
    print("Failed to connect to Ganache")
    exit()

print("Connected to Ganache")

# 读取合约源代码
try:
    with open('0x06012c8cf97bead5deae237070f9587f8e7a266d.sol','r') as file:
        contract_source_code = file.read()
except FileNotFoundError:
    print("Failed to read contract source code.")
    exit()

# 提取Solidity版本
version_match = re.search(r'pragma solidity \^?([0-9]+\.[0-9]+\.[0-9]+);', contract_source_code)
if version_match:
    version = version_match.group(1)
    print(f"Extracted Solidity version: {version}")
else:
    print("No valid Solidity version found.")
    exit()

# 使用solc编译合约
solcx.install_solc(version)  # 安装提取的solc版本
compiled_sol = solcx.compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:SimpleContract']
# 获取账户
account = web3.eth.accounts[0]
print(f"Using account: {account}")

# 部署合约
def deploy_contract():
    # 创建合约构造函数
    SimpleContract = web3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )

    # 构建交易
    tx_hash = SimpleContract.constructor().transact({'from': account})

    # 等待交易确认
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    print(f"Contract deployed at address: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

# 调用部署函数
contract_address = deploy_contract()

# 创建合约实例
contract = web3.eth.contract(address=contract_address, abi=contract_interface['abi'])

# 读取合约状态
def read_contract_data():
    count = contract.functions.count().call()
    print(f"Count value: {count}")

# 发送交易调用合约的写函数
def increment_count():
    tx_hash = contract.functions.increment().transact({'from': account})
    web3.eth.waitForTransactionReceipt(tx_hash)
    print("Count incremented.")

# 示例调用
read_contract_data()
increment_count()
read_contract_data()