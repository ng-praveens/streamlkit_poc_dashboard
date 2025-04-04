import openai
import json
import re
from dotenv import load_dotenv
import os
import boto3
from apps.email_home.logger_config import logger

# Load environment variables
load_dotenv()
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = OPENAI_API_KEY

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")


def get_email_sequence(prompt):
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    # modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
    # messages = [
    #     {"role": "user", "content": "You are an expert email marketer."},
    #     {"role": "assistant", "content": prompt},
    # ]
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.1,
            "top_k": 250,
            "top_p": 0.999,
            "messages": messages,
        }
    )

    response = bedrock.invoke_model(modelId=modelId, body=body)
    logger.info(response)
    response_body = json.loads(response.get("body").read())
    logger.info(response_body)
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are an expert email marketer."},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # content = response_body["choices"][0]["message"]["content"]
    content = response_body["content"][0]["text"]

    emails = re.findall(r"Email \d:.*?(?=\nEmail \d:|$)", content, re.DOTALL)
    email_dict = {}

    for email in emails:
        email_number_match = re.search(r"Email (\d):", email)
        subject_line_match = re.search(r"Subject Line:\s*(.*?)\n", email)
        body_match = re.search(r"Subject Line:\s*.*?\n\n(.*)", email, re.DOTALL)

        if email_number_match and subject_line_match and body_match:
            email_number = email_number_match.group(1)
            subject_line = subject_line_match.group(1).strip()
            body = body_match.group(1).strip()

            email_dict[f"Email {email_number}"] = {
                "Subject Line": subject_line,
                "Body": body,
            }

    return json.dumps(email_dict)
