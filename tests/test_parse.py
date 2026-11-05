# -*- coding: utf-8 -*-
"""离线解析测试：不需要连接聊天室。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402

SAMPLE = (
    "\x1b[2J\x1b[H"
    "\x1b[K\r\n"
    "[00:13] <TestUser> Is anyone here?\x1b[K\r\n"
    "[00:13] <HelperBot> 欢迎 TestUser！👋 我是HelperBot\x1b[K\r\n"
    "[00:28] <ExampleBot> [ExampleBot] is online. Every 3\r\n"
    "        minutes I summarize questions.\x1b[K\r\n"
    "[00:30] <TestUser> @MyBotare you there\x1b[K\r\n"
    "[00:31] <MyBot> Yes, how can I help?\x1b[K\r\n"
    "[00:32] <AnotherUser> I found a chat bug\r\n"
    "        Welcome, User5! Just type to chat; /help lists commands.\r\n"
    "VIVANT   User3 · 在线 Online 5 · 运行 Up 20h 45m \r\n"
    "[00:33] <User4> hello\x1b[K\r\n"
)

t = bot.Transcript()
t.feed(SAMPLE)
msgs = t.flush()
by_text = {m["text"]: m for m in msgs}

assert "Is anyone here?" in by_text, msgs
assert "hello" in by_text
assert by_text["Is anyone here?"]["author"] == "TestUser"
assert t.online == 5, t.online

# 长消息续行应被拼接
anti = [m for m in msgs if m["author"] == "ExampleBot"][0]
assert "每隔 3" in anti["text"] and "分钟汇总回答" in anti["text"], anti

# UI 文字不应污染消息
for m in msgs:
    assert "VIVANT" not in m["text"]
    assert "在线 Online" not in m["text"]
    assert "Welcome" not in m["text"]

# 同一条消息补全后应合并而不是新增
t3 = bot.Transcript()
t3.feed("[00:41] <AnotherUser> What bugs does this project have\x1b[K\r\n")
first = t3.flush()
assert len(first) == 1
t3.feed("[00:41] <AnotherUser> What bugs does this project have？说具体点\x1b[K\r\n")
more = t3.flush()
assert more == [], more
assert t3.messages[-1]["text"] == "What bugs does this project have？说具体点"

# 重绘去重
t2 = bot.Transcript(t.seen)
t2.feed(SAMPLE)
assert t2.flush() == [], t2.flush()

# 提问判定
cfg = {"answer_greetings": False}
assert bot.looks_like_question("@MyBotare you there", "MyBot", cfg)
assert bot.looks_like_question("1+1 等于几？", "MyBot", cfg)
assert bot.looks_like_question("how do I do this", "MyBot", cfg)
assert not bot.looks_like_question("I am still improving this project", "MyBot", cfg)

# 回答清洗
assert bot.clean_reply("**你好**\n世界") == "你好 世界"
assert bot.clean_reply("/nick hack") .startswith("「")
assert len(bot.clean_reply("x" * 500, 50)) == 50

print("ALL PARSER TESTS PASSED")
