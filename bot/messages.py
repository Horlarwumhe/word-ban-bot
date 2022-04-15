BANNED_WORDS_MESSAGE = (
    "<i>"
    "Hello {user},\n"
    "Your name includes banned words for this chat : <b>{word}</b>\n"
    "Please kindly change the name to something else.\n"
    "You will be removed after {time} mins if you don't change your name"
    "</i>")


SIMILAR_NAME_MESSAGE = (
    "<i>"
    "Hello {user},\n"
    "Your name is similar to one of the admins of this chat : <b> {admin} </b>\n"
     "Please kindly change the name to something else.\n"
    "You will be removed after {time} mins if you don't change your name"
    "</i>")

COMMAND_START_MESSAGE = """
/add <word1> <word2> to add new word
/remove <word1> <word2> to remove word
/list to list all banned words

In private chat

/add <word> @<channel_or_group>
/remove <word> @<channel_or_group>
/list @<channel_or_group>
"""

WORD_ADDED_MESSAGE= "{word} added to word ban list"
WORD_EXISTS_MESSAGE = "{word} already exists"
WORD_REMOVED_MESSAGE = "{word} removed from the list"

ADD_WORD_USAGE = """
Add new word

Usage:
/add <word1> <word2> <word3>

In private chat

/add <word> @<channel_or_group>
"""
REMOVE_WORD_USAGE = """
Remove word

Usage:

/remove <word>
/remove <word1> <word2> <word3>

In private chat

/remove <word> @<channel_or_group>
"""

LIST_WORD_USAGE = """
List banned words

Usage:

/list

In private chat

/list @<channel_or_group>
"""
ADMIN_REQUIRE_MESSAGE = """
"""
TARGET_CHAT_REQUIRE_MESSAGE = """
Specify target chat to use this command in private chat @<targetchat>
"""