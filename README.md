## Medea - Chatbot engine in Python 3.x

Tired of Cortana, Google, or Alexa, spying on you? Would you prefer to make your own cute virtual assistant waifu?
MEDEA is for you!

MEDEA is a chatbot engine that runs in Python 3.x. It's based in the classic ALICE AI model, which
uses XML patterns to construct rules for each sentence. These rules consist of a Pattern, and
one or several possible replies. When an user inputs some text that matches a pattern, MEDEA
will return a reply based on that pattern. It's that simple!

You can't actually do much right now as it's in early development, but you can extend her
functionalities a bit if you know Python. It's very simplistic, honestly.

## Prerequisites

- Python 3.6+
- That's all!

## How to use Medea

Just drag and drop the files anywhere in your system. Edit the config.json to set the name of your
bot and yours, as well as the AI.json file inside the chatbot folder.

Edit the BIOS.pyb inside the chatbot folder to add your own rules. There are a few implemented
so you will know how it works. When adding patterns, the available wildcards are:

\_ Matches only ONE word (Any)

\* Matches ONE OR MORE words

\? Matches ONE OR NONE words

\^ Matches NONE OR ANY words (Anything)

(WORD1|WORD2|...|WORDN) Matches ONE OF THE WORDS inside. You can insert from two to any words you'd like.


# Some pattern examples:

I LIKE DOING * IN THE MORNING
(This will match "I like doing exercise in the morning", and "I like doing some sports in the morning")

I WANT TO BE _
(This matches "I want to be loved", but won't match "I want to be the best").

I CAN ?
(This matches "I can" as well as "I can fly", but won't match "I can do laundry")

To run medea, simply call the medea.py file from your command line, like
$ python medea.py
