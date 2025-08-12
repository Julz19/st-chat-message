import os
from typing import Optional, Union

import streamlit.components.v1 as components

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

_RELEASE = True
COMPONENT_NAME = "st_chat_message"

# use the build instead of development if release is true
if _RELEASE:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, "frontend/out")

    _st_chat_message = components.declare_component(
        COMPONENT_NAME,
        path=build_dir
    )
else:
    _st_chat_message = components.declare_component(
        COMPONENT_NAME,
        url="http://localhost:3000/component/st_chat_message.st_chat_message"
    )

# data type for avatar style
AvatarStyle = Literal[
    "adventurer",
    "adventurer-neutral",
    "avataaars",
    "avataaars-neutral",
    "big-ears",
    "big-ears-neutral",
    "big-smile",
    "bottts",
    "bottts-neutral",
    "croodles",
    "croodles-neutral",
    "fun-emoji",
    "icons",
    "identicon",
    "initials",
    "lorelei",
    "lorelei-neutral",
    "micah",
    "miniavs",
    "open-peeps",
    "personas",
    "pixel-art",
    "pixel-art-neutral",
    "shapes",
    "thumbs",
]


def message(message: str,
            is_user: Optional[bool] = False,
            avatar_style: Optional[AvatarStyle] = None,
            logo: Optional[str] = None,
            seed: Optional[Union[int, str]] = 88,
            key: Optional[str] = None,
            partial: Optional[bool] = False,
            rich_content: Optional[bool] = True):
    """
    Creates a new instance of streamlit-chat component

    Parameters
    ----------
    message: str
        The message to be displayed in the component
    is_user: bool
        if the sender of the message is user, if `True` will align the
        message to right, default is False.
    avatar_style: Literal or None
        The style for the avatar of the sender of message, default is bottts
        for not user, and pixel-art-neutral for user.
        st-chat uses https://www.dicebear.com/styles for the avatar
    logo: Literal or None
        The logo to be used if we do not wish Avatars to be used. This is useful
        if we want the chatbot to be branded
    seed: int or str
        The seed for choosing the avatar to be used, default is 42.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    partial: bool or None
        Indicates that the message is partial, and will be updated later (for
        example, if the message is being streamed).
    rich_content: bool or None
        When True, render content as rich Markdown (with LaTeX, tables, code highlighting).
        When False, render as plain text for fastest incremental updates.

    Returns: None
    """
    if logo:
        _st_chat_message(
            message=message,
            seed=seed,
            isUser=is_user,
            logo=logo,
            key=key,
            partial=partial,
            richContent=rich_content,
        )
    else:
        if not avatar_style:
            avatar_style = "fun-emoji" if is_user else "bottts"
        _st_chat_message(
            message=message,
            seed=seed,
            isUser=is_user,
            avatarStyle=avatar_style,
            key=key,
            partial=partial,
            richContent=rich_content,
        )


from typing import Iterable  # noqa: E402
import time  # noqa: E402

def message_stream(
    chunks: "Iterable[str]",
    *,
    is_user: Optional[bool] = False,
    avatar_style: Optional[AvatarStyle] = None,
    logo: Optional[str] = None,
    seed: Optional[Union[int, str]] = 88,
    key: Optional[str] = None,
    rich_content: Optional[bool] = True,
    throttle_ms: int = 0,
    flush_every: int = 1,
    initial_text: str = "",
) -> str:
    """Stream content to a single chat message, similar to Streamlit's docs helpers.

    This helper consumes an iterator of string deltas and incrementally updates a
    single chat message in-place by repeatedly calling `message(..., partial=True)`
    with a stable `key`. On completion, it finalizes the message with
    `partial=False` and returns the final text.

    Parameters
    ----------
    chunks: Iterable[str]
        An iterable/generator yielding text deltas to append.
    is_user: bool
        Whether to render as a user message.
    avatar_style: AvatarStyle or None
        Avatar style when not providing a logo.
    logo: str or None
        URL/path for a custom logo image, bypassing avatar style.
    seed: int | str
        Seed for avatar generation.
    key: str or None
        Stable Streamlit component key for in-place updates. Strongly recommended.
    rich_content: bool
        Use Markdown rendering (True) or plain text (False) for speed.
    throttle_ms: int
        Minimum milliseconds between UI updates (0 to update every eligible chunk).
    flush_every: int
        Emit an update every N chunks to reduce re-render frequency (default 1).
    initial_text: str
        Optional initial text to seed the message with before streaming.

    Returns
    -------
    str
        The final accumulated text.
    """
    accumulated_text = initial_text or ""
    last_emit_ts = 0.0
    chunks_since_emit = 0

    # Ensure an initial render so the placeholder appears quickly
    message(
        accumulated_text,
        is_user=is_user,
        avatar_style=avatar_style,
        logo=logo,
        seed=seed,
        key=key,
        partial=True,
        rich_content=rich_content,
    )

    for delta in chunks:
        if delta is None:
            continue
        if not isinstance(delta, str):
            delta = str(delta)
        if not delta:
            continue

        accumulated_text += delta
        chunks_since_emit += 1

        now = time.monotonic()
        should_flush_count = flush_every > 0 and (chunks_since_emit % flush_every == 0)
        should_flush_time = throttle_ms <= 0 or ((now - last_emit_ts) * 1000.0 >= throttle_ms)
        if should_flush_count and should_flush_time:
            message(
                accumulated_text,
                is_user=is_user,
                avatar_style=avatar_style,
                logo=logo,
                seed=seed,
                key=key,
                partial=True,
                rich_content=rich_content,
            )
            last_emit_ts = now

    # Finalize message
    message(
        accumulated_text,
        is_user=is_user,
        avatar_style=avatar_style,
        logo=logo,
        seed=seed,
        key=key,
        partial=False,
        rich_content=rich_content,
    )

    return accumulated_text

