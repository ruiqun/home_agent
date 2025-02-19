# models/qwen_model.py

import torch, logging
from transformers import AutoModelForCausalLM, AutoTokenizer

class QwenModel:
    def __init__(self, model_path):
        self.model_path = model_path
        logging.debug("Starting model loading...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, device_map="auto", trust_remote_code=True).eval()
            logging.debug("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise

    def generate_reply(self, input_text):
        try:
            # 对输入文本进行分词
            input_ids = self.tokenizer(input_text, return_tensors='pt').input_ids.to(self.model.device)

            # 生成文本
            with torch.no_grad():
                output = self.model.generate(input_ids, max_new_tokens=512, do_sample=True, top_p=0.85, temperature=0.35)

            # 解码生成的文本
            reply_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            return reply_text
        except Exception as e:
            print(f"调用本地 Qwen 模型时出现异常: {e}")
            return "抱歉，暂时无法获取回复，请稍后再试。"