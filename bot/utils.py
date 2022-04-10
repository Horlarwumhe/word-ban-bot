from bot.db import DB

BANNED_WORDS_MESSAGE = (
    'Hello {user}, Your {type}, {name}\n'
    'is among the banned words for this chat\n'
    '{word} is banned in this chat'
    "kindly change the name to something else.\n"
    "You will be removed after 5 mins if you dont change your name")


def check_banned_words(name):
    found = None
    name = ''.join(filter(str.isalpha, name)).lower()
    with DB() as db:
        cur = db.execute('select word from banned_words where id > 0')
        banned_words = [row['word'].lower() for row in cur]
        for word in banned_words:
            if word in name:
                found = word
                break
    return found


def check_admin_names(admin_names, name):
    # remove no alphabetic character ,eg, _
    username = ''.join(filter(str.isalpha, name)).lower()
    print(username,admin_names)

    for admin in admin_names:
        try:
            fname, lname = map(str.lower,admin.split())
        except ValueError:
            fname = lname = admin.split()[0].lower()
        print(fname,lname)
        if fname in username or lname in username:
            print('found ',username,' in admin ',fname,'-',lname)
            return admin
    return None


def list_admin_names(bot, chat_id):
    admins = bot.get_chat_administrators(chat_id)
    admins = [
        "%s %s" % (u.user.first_name or '', u.user.last_name or '')
        for u in admins
    ]
    return admins
