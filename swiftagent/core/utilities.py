def hash_url(url):
    from base64 import urlsafe_b64encode

    return (
        urlsafe_b64encode(url.encode())
        .decode()
        .rstrip("=")
        .replace("/", "_")
        .replace("+", "-")
    )


def unhash_url(hashed):
    from base64 import urlsafe_b64decode

    padded = hashed.replace("_", "/").replace("-", "+") + "=" * (
        -len(hashed) % 4
    )
    return urlsafe_b64decode(padded.encode()).decode()


# Example usage:
# url = "https://example.com/long/path?param=value"
# encoded = hash_url(url)
# decoded = unhash_url(encoded)
# assert url == decoded  # Will pass
