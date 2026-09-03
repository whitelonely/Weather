import logging
import os
import json

class NoStaticFilter(logging.Filter):
    """过滤掉静态资源的请求日志"""
    def filter(self, record):
        return 'GET /static/' not in record.getMessage()

logging.getLogger('werkzeug').addFilter(NoStaticFilter())

def _load_city_map():
    """从 data/city_map.json 加载城市中英文映射表"""
    try:
        # 获取当前文件所在目录（config.py 所在目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 指向 data 子文件夹
        json_path = os.path.join(current_dir, 'data', 'city_map.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("警告: data/city_map.json 文件未找到，城市映射表为空")
        return {}
    except json.JSONDecodeError:
        print("警告: data/city_map.json 格式错误，城市映射表为空")
        return {}

# 加载城市映射表（供其他模块导入使用）
CITY_NAME_MAP = _load_city_map()