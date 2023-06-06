from dataclasses import dataclass, field

from pistachio.utils import hash_password


@dataclass
class User:
    id: int = field(init=False, default=0)
    username: str
    email: str
    nickname: str
    password: str = ""
    avatar: str = "https://i.pravatar.cc/150?img=2"
    bio: str = ""
    followings: list = field(default_factory=list)
    followers: list = field(default_factory=list)
    posts: list = field(default_factory=list)

    def __post_init__(self):
        self.password_hash = hash_password(self.password)


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
