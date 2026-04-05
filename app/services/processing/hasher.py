import hashlib


class Hasher:
    def sha256(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()