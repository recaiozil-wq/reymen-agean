"""A2A prototip birim testleri."""

from __future__ import annotations

import threading
import time

import pytest

from reymen.a2a import (
    A2AError,
    Agent,
    Broker,
    Message,
    MessageType,
)


class TestMessage:
    def test_message_defaults(self):
        msg = Message(sender="alice", receiver="bob", content="hello")
        assert msg.sender == "alice"
        assert msg.receiver == "bob"
        assert msg.content == "hello"
        assert msg.type == MessageType.TEXT
        assert msg.id  # otomatik ID
        assert msg.timestamp > 0

    def test_message_reply(self):
        msg = Message(sender="alice", receiver="bob", content="hello")
        reply = msg.reply("hi back")
        assert reply.sender == "bob"
        assert reply.receiver == "alice"
        assert reply.content == "hi back"
        assert reply.reply_to == msg.id
        assert reply.type == MessageType.RESPONSE

    def test_message_as_dict(self):
        msg = Message(sender="a", receiver="b", content="x")
        d = msg.as_dict()
        assert d["sender"] == "a"
        assert d["receiver"] == "b"
        assert d["type"] == "text"


class TestBroker:
    def test_register_and_unregister(self):
        broker = Broker()
        broker.register("agent1")
        assert broker.is_registered("agent1")
        broker.unregister("agent1")
        assert not broker.is_registered("agent1")

    def test_send_to_unregistered_raises(self):
        broker = Broker()
        msg = Message(sender="a", receiver="ghost", content="x")
        with pytest.raises(A2AError, match="kayıtlı değil"):
            broker.send(msg)

    def test_send_and_receive(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        msg = Message(sender="alice", receiver="bob", content="hello")
        broker.send(msg)
        received = broker.receive("bob", block=False)
        assert received is not None
        assert received.content == "hello"

    def test_receive_empty_non_blocking(self):
        broker = Broker()
        broker.register("alice")
        assert broker.receive("alice", block=False) is None

    def test_receive_unregistered_raises(self):
        broker = Broker()
        with pytest.raises(A2AError):
            broker.receive("ghost", block=False)

    def test_peek(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.send(Message(sender="alice", receiver="bob", content="msg1"))
        peeked = broker.peek("bob")
        assert peeked is not None
        assert peeked.content == "msg1"
        # Peek silmez
        assert broker.inbox_size("bob") == 1

    def test_inbox_size(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.send(Message(sender="alice", receiver="bob", content="m1"))
        broker.send(Message(sender="alice", receiver="bob", content="m2"))
        assert broker.inbox_size("bob") == 2

    def test_broadcast(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.register("carol")
        sent_to = broker.broadcast("alice", "announcement")
        assert "bob" in sent_to
        assert "carol" in sent_to
        assert "alice" not in sent_to
        assert broker.inbox_size("bob") == 1
        assert broker.inbox_size("carol") == 1

    def test_broadcast_with_exclude(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.register("carol")
        sent_to = broker.broadcast("alice", "msg", exclude={"bob"})
        assert "bob" not in sent_to
        assert "carol" in sent_to

    def test_message_log(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.send(Message(sender="alice", receiver="bob", content="m1"))
        broker.send(Message(sender="bob", receiver="alice", content="m2"))
        log = broker.message_log()
        assert len(log) == 2

    def test_stats(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.send(Message(sender="alice", receiver="bob", content="x"))
        stats = broker.stats()
        assert stats["agents"] == 2
        assert stats["total_messages"] == 1
        assert stats["pending"]["bob"] == 1

    def test_reset(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        broker.send(Message(sender="alice", receiver="bob", content="x"))
        broker.reset()
        assert broker.inbox_size("bob") == 0
        assert len(broker.message_log()) == 0

    def test_handler_called(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        received = []
        broker.set_handler("bob", lambda msg: received.append(msg))
        broker.send(Message(sender="alice", receiver="bob", content="hi"))
        assert len(received) == 1
        assert received[0].content == "hi"

    def test_clear_handler(self):
        broker = Broker()
        broker.register("alice")
        broker.register("bob")
        received = []
        broker.set_handler("bob", lambda msg: received.append(msg))
        broker.clear_handler("bob")
        broker.send(Message(sender="alice", receiver="bob", content="hi"))
        assert len(received) == 0


class TestAgent:
    def test_agent_creation_registers(self):
        broker = Broker()
        agent = Agent("test", broker)
        assert broker.is_registered("test")

    def test_agent_send_and_receive(self):
        broker = Broker()
        alice = Agent("alice", broker)
        bob = Agent("bob", broker)
        alice.send("bob", "hello")
        msg = bob.receive(block=False)
        assert msg is not None
        assert msg.content == "hello"

    def test_agent_reply(self):
        broker = Broker()
        alice = Agent("alice", broker)
        bob = Agent("bob", broker)
        original = alice.send("bob", "question")
        msg = bob.receive(block=False)
        bob.reply(msg, "answer")
        reply = alice.receive(block=False)
        assert reply is not None
        assert reply.content == "answer"
        assert reply.reply_to == original.id

    def test_agent_broadcast(self):
        broker = Broker()
        alice = Agent("alice", broker)
        bob = Agent("bob", broker)
        carol = Agent("carol", broker)
        sent_to = alice.broadcast("team update")
        assert "bob" in sent_to
        assert "carol" in sent_to

    def test_agent_peek(self):
        broker = Broker()
        alice = Agent("alice", broker)
        bob = Agent("bob", broker)
        alice.send("bob", "msg")
        peeked = bob.peek()
        assert peeked is not None
        assert bob.inbox_size == 1

    def test_agent_close(self):
        broker = Broker()
        agent = Agent("temp", broker)
        agent.close()
        assert not broker.is_registered("temp")

    def test_agent_on_message_callback(self):
        broker = Broker()
        received = []
        bob = Agent("bob", broker, on_message=lambda msg: received.append(msg))
        alice = Agent("alice", broker)
        alice.send("bob", "callback test")
        assert len(received) == 1
        assert received[0].content == "callback test"

    def test_agent_repr(self):
        broker = Broker()
        agent = Agent("x", broker)
        assert "x" in repr(agent)


class TestConcurrency:
    def test_concurrent_send_receive(self):
        """Birden fazla thread'in aynı broker'a mesaj göndermesi."""
        broker = Broker()
        broker.register("receiver")
        received = []
        lock = threading.Lock()

        def sender(n):
            agent = Agent(f"sender-{n}", broker)
            for i in range(10):
                agent.send("receiver", f"msg-{n}-{i}")

        threads = [threading.Thread(target=sender, args=(n,)) for n in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 5 sender * 10 msg = 50 mesaj
        assert broker.inbox_size("receiver") == 50

    def test_blocking_receive_with_timeout(self):
        """Blocking receive timeout ile None döner."""
        broker = Broker()
        broker.register("alice")
        result = broker.receive("alice", timeout=0.1, block=True)
        assert result is None