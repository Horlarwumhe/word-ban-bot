export PYTHONUNBUFFERED=1
export BOT_TOKEN=""
cd $HOME/word-ban-bot
mkdir -p logs
pip3 install -r requirements.txt
python3 main.py
