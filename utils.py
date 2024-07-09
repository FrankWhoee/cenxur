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