To install on Windows
# Install Python
# install Ollama  (which http://www.ollama.com) 

You need source and python (install python first)

# 1 Create a virtual enviroment
 py -m venv .venv

# 2 Activate it. (to deactivate it "deactivate")
.venv\Scripts\activate

# install needed libies
py -m pip install -r requirements.txt

py jafuChat.py




## To install on mac ##

# Install Python
# Install Xcode
# install Ollama  (which http://www.ollama.com) 


# create environment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python jafuChat.py 


#deactivate
source .venv/bin/deactivate