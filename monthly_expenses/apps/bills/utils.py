from hashlib import sha256


def generate_hash_from_image(image_binary_file):
    """
    Generate sha256 using binary contents of the image
    """
    CHUNK_SIZE = 1024
    sha256_hash = sha256()
    image_binary_file.seek(0)
    while(True):
        chunk = image_binary_file.read(CHUNK_SIZE)
        if not chunk: break
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()
  