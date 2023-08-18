from dataclasses import dataclass, field

from pistachio.utils import generate_alnum, hash_password


@dataclass
class User:
    id: int = field(init=False, default=0)
    email: str = ""
    password: str = ""
    username: str = ""
    nickname: str = ""
    avatar: str = "https://i.pravatar.cc/150?img=2"
    bio: str = ""
    followings: list = field(default_factory=list)
    followers: list = field(default_factory=list)
    posts: list = field(default_factory=list)

    def __post_init__(self):
        self.password_hash = hash_password(self.password)
        if not self.username:
            self.username = generate_alnum(20)


@dataclass
class Attachment:
    id: int = field(init=False, default=0)
    name: str
    size: int
    url: str
    post: "Post" = field(init=False)


@dataclass
class Post:
    id: int = field(init=False, default=0)
    user: User
    attachment: Attachment
    description: str = ""
