# 用于处理本地已有文件（清理或展示）
import os
import re
import json

# 获取合约的ABI和源码,并删除源码中空格与注释
def get_contract_data():
    with open('data_source_code.json') as f:
        data_source_code = json.load(f)
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

def clean_abi(abi):
    return json.dumps(abi, indent=4)

if __name__ == '__main__':
    source_code, abi = get_contract_data()
    cleaned_code, code_lines = clean_source_code(source_code)
    print(abi)



    