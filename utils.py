import re

def get_urls(s):
    url_pattern = "https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"
    return re.findall(url_pattern, s)

def is_url(s):
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    return re.match(url_pattern, s) is not None

def create_env_template():
  """Creates a template .env file with placeholder comments."""
  template_content = """
# This is a template .env file. Please replace the placeholders with your actual values.

# Production API key
PROD_KEY=""

# Development API key
DEV_KEY=""

# Current environment (prod or dev)
ENVIRONMENT=""
"""

  with open(".env", "w") as f:
    f.write(template_content)