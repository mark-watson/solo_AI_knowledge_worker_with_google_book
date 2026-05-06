# Using Gemini with images

Start by installing the Python requirements in requirements.txt

Run:

    python photo_understanding.py

The output looks like:

```json
[
  {"box_2d": [204, 156, 467, 348], "label": "a man with a grey sweater and black shirt is sitting at a table"},
  {"box_2d": [255, 0, 998, 331], "label": "a man with a black baseball cap is sitting at a table"},
  {"box_2d": [178, 596, 998, 998], "label": "a man with a green shirt is sitting at a table"},
  {"box_2d": [257, 734, 525, 875], "label": "a woman with a white shirt and a purple scarf is sitting at a table"},
  {"box_2d": [198, 435, 393, 629], "label": "a woman with a red scarf is sitting at a table"}
]
```

```json
[
  {"box_2d": [179, 597, 1000, 1000], "label": "a man sitting at a table playing cards with four other people. He is holding cards in his left hand."},
  {"box_2d": [206, 150, 469, 348], "label": "a man sitting at a table playing cards. He is holding a card in his right hand."},
  {"box_2d": [256, 739, 523, 875], "label": "a woman sitting at a table playing cards."},
  {"box_2d": [198, 437, 389, 628], "label": "a woman sitting at a table playing cards. She is holding a card in her right hand."},
  {"box_2d": [254, 0, 1000, 327], "label": "a man sitting at a table playing cards. He is holding a card in his right hand."}
]
```