from google.genai import types
import inspect

print("Fields in ThinkingConfig:")
try:
    print(types.ThinkingConfig.model_fields.keys())
except:
    print(dir(types.ThinkingConfig))
