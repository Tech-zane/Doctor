from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyAKrjlFMQQxVyyqe_i1wcvWM4JVGCZ_X4E")

sys_instruction = "You are a cat called Missy"

response = client.models.generate_content(
    model = 'gemini-2.0-flash',
    config = types.GenerateContentConfig(system_instruction= sys_instruction),
    contents = ["who is the president now"]
)

print(response.text)