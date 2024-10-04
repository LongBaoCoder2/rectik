from functools import wraps

magic_dir = 'merlin'

def magicdir(f):
    artifact = 'magicdir'
    @wraps(f)
    def func(self):
        from io import BytesIO
        from tarfile import TarFile
        existing = getattr(self, artifact, None)
        if existing:
            buf = BytesIO(existing)
            with TarFile(mode='r', fileobj=buf) as tar:
                tar.extractall()
        f(self)
        buf = BytesIO()
        with TarFile(mode='w', fileobj=buf) as tar:
            tar.add(magic_dir)
        setattr(self, artifact, buf.getvalue())
    return func