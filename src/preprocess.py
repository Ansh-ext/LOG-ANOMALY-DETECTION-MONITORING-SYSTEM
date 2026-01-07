import re

def preprocess_log(message: str) -> str:

    message = re.sub(r'blk[_-]?\d+', '<block_id>', message)
    message = re.sub(r'\b\d{1,3}(\.\d{1,3}){3}\b', '<ip>', message)
    message = re.sub(r'\b\d{4,5}\b', '<port>', message)
    message = re.sub(r'\b\d{6,}\b', '<large_num>', message)
    message = re.sub(r'\b\d+\b', '<num>', message)

    message = message.lower()

    message = re.sub(r'\s+', ' ', message).strip()

    return message
  
