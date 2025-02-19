import torch
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
from accelerate import init_empty_weights, load_checkpoint_and_dispatch
from accelerate.utils import infer_auto_device_map

from utils.config import LOCAL_QWEN_MODEL_PATH

# 本地模型路径
local_model_path = LOCAL_QWEN_MODEL_PATH

try:
    # 从本地加载分词器
    tokenizer = AutoTokenizer.from_pretrained(local_model_path, trust_remote_code=True)

    # 从本地加载模型配置
    config = AutoConfig.from_pretrained(local_model_path, trust_remote_code=True)

    # 初始化空的模型
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config, trust_remote_code=True)

    # 推断自动设备映射
    max_memory = {0: "1GB", "cpu": "16GB", "disk": "100GB"}  # 根据实际情况调整内存大小
    device_map = infer_auto_device_map(model, max_memory=max_memory, no_split_module_classes=model._no_split_modules)

    # 加载并分发模型
    model = load_checkpoint_and_dispatch(
        model,
        local_model_path,
        device_map=device_map,
        offload_folder="offload",
        offload_buffers=True
    )
    model = model.eval()

    print("Qwen-7B-Chat 模型和分词器已从本地加载并进行设备分发。")
except Exception as e:
    print(f"加载模型和分词器时出现错误: {e}")