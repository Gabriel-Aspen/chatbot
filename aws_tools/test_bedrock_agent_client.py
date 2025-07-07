from aws_tools.bedrock_kb_client import get_knowledge_base_by_name
import json

if __name__ == "__main__":
    kb_name = "test-knowledge-base"
    kb_info = get_knowledge_base_by_name(kb_name)
    if kb_info:
        print(json.dumps(kb_info, indent=2, default=str))
    else:
        print(f"Knowledge base '{kb_name}' not found.") 