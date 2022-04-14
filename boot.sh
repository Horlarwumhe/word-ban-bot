

DAEMON_DIR=$HOME/.config/systemd/user.control
# create directory for user systemd files
mkdir -p $DAEMON_DIR

#move the unit file to the diretory systemd will search
cp $HOME/word-ban-bot/word-ban-bot.service $DAEMON_DIR/word-ban-bot.service
systemctl --user enable word-ban-bot
systemctl --user stop word-ban-bot 
systemctl --user start word-ban-bot 