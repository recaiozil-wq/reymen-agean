"""
Platform adapters for messaging integrations.

Each adapter handles:
- Receiving messages from a platform
- Sending messages/responses back
- Platform-specific authentication
- Message formatting and media handling
"""

from .base import BasePlatformAdapter, MessageEvent, SendResult

# QQAdapter and YuanbaoAdapter were previously imported eagerly here, but
# nothing in the codebase consumes ``from reymen.gateway.platforms import
# QQAdapter`` (every real call site uses the long-form path
# ``from reymen.gateway.platforms.qqbot import QQAdapter``). The eager imports
# pulled in qqbot's chunked-upload + keyboards + onboard machinery and
# yuanbao's websocket stack — about 48 ms wall and ~8 MB RSS on every
# CLI invocation, even ones that never touch a gateway adapter.
#
# Use PEP 562 module ``__getattr__`` to keep the public re-export working
# while deferring the actual import to first attribute access. This is
# 100% backward-compatible for any external code that still imports the
# adapters from the package root.
__all__ = [
    "BasePlatformAdapter",
    "MessageEvent",
    "SendResult",
    "SlackAdapter",
    "GoogleChatAdapter",
    "HomeAssistantAdapter",
    "MattermostAdapter",
    "BlueBubblesAdapter",
    "SignalAdapter",
    "MatrixAdapter",
    "DingTalkAdapter",
    "FeishuAdapter",
    "WeComAdapter",
    "QQAdapter",
    "TeamsAdapter",
    "YuanbaoAdapter",
    "WhatsAppAdapter",
]


def __getattr__(name):
    if name == "SlackAdapter":
        from .slack import SlackAdapter  # noqa: F401
        return SlackAdapter
    if name == "GoogleChatAdapter":
        from .google_chat import GoogleChatAdapter  # noqa: F401
        return GoogleChatAdapter
    if name == "HomeAssistantAdapter":
        from .homeassistant import HomeAssistantAdapter  # noqa: F401
        return HomeAssistantAdapter
    if name == "MattermostAdapter":
        from .mattermost import MattermostAdapter  # noqa: F401
        return MattermostAdapter
    if name == "BlueBubblesAdapter":
        from .bluebubbles import BlueBubblesAdapter  # noqa: F401
        return BlueBubblesAdapter
    if name == "SignalAdapter":
        from .signal import SignalAdapter  # noqa: F401
        return SignalAdapter
    if name == "MatrixAdapter":
        from .matrix import MatrixAdapter  # noqa: F401
        return MatrixAdapter
    if name == "DingTalkAdapter":
        from .dingtalk import DingTalkAdapter  # noqa: F401
        return DingTalkAdapter
    if name == "FeishuAdapter":
        from .feishu import FeishuAdapter  # noqa: F401
        return FeishuAdapter
    if name == "WeComAdapter":
        from .wecom import WeComAdapter  # noqa: F401
        return WeComAdapter
    if name == "QQAdapter":
        from .qqbot import QQAdapter  # noqa: F401
        return QQAdapter
    if name == "TeamsAdapter":
        from .teams import TeamsAdapter  # noqa: F401
        return TeamsAdapter
    if name == "YuanbaoAdapter":
        from .yuanbao import YuanbaoAdapter  # noqa: F401
        return YuanbaoAdapter
    if name == "WhatsAppAdapter":
        from .whatsapp import WhatsAppAdapter  # noqa: F401
        return WhatsAppAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)
