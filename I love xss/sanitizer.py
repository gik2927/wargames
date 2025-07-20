import bleach

ALLOWED_TAGS = ['script']   #I only love script tags!
ALLOWED_ATTRIBUTES = {}
ALLOWED_PROTOCOLS = ['http', 'https']

def sanitize_input(user_input: str) -> str:
    return bleach.clean(
        user_input,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True
    )