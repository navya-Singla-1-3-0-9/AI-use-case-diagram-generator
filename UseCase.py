import re
import spacy
from PIL import Image, ImageDraw, ImageFont

# python -m spacy download en

def segmentation(text):
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D","Ph<prd>D")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def tokenization(doc):

    doc = segmentation(doc)
    tokenized_text = []
    for line in doc:
        tokenized_text.append(line.split())
    return tokenized_text



def posTag(doc):

    doc = segmentation(doc)
    nlp = spacy.load('en_core_web_sm',disable=['ner','textcat'])
    tagged_text = []
    for line in doc:
        sub = []
        t = nlp(line)
        for token in t:
            if token.pos_ == 'PUNCT':
                continue
            sub.append(token.text+'->'+token.pos_)
        tagged_text.append(sub)
    return tagged_text



def lemmatization(doc):

    doc = segmentation(doc)
    nlp = spacy.load('en_core_web_sm',disable=['ner','textcat'])
    lemmatized_text = []
    for line in doc:
        sub = []
        t = nlp(line)
        for token in t:
            if token.pos_ == 'PUNCT':
                continue
            sub.append(token.lemma_)
        lemmatized_text.append(sub)
    return lemmatized_text
    


def knowledgeExtract(doc):

    doc = segmentation(doc)
    use_case = {}
    nlp = spacy.load('en_core_web_sm')
    prev_actors = []
    for line in doc:
        pos_text = nlp(line)
        names = [ent.text for ent in pos_text.ents]
        c = 0
        flag = True
        while c < len(pos_text):
            actors = set()
            while c < len(pos_text):
                if (pos_text[c].pos_ == 'NOUN' or pos_text[c].pos_ == 'PROPN') and pos_text[c].dep_ == 'compound':
                    if pos_text[c+1].text not in names:
                        actors.add((pos_text[c].lemma_ + " " + pos_text[c+1].lemma_).title())
                    c += 1
                elif (pos_text[c].pos_ == 'NOUN' or pos_text[c].pos_ == 'PROPN'):
                    if pos_text[c].text not in names:
                        actors.add(pos_text[c].lemma_.title())
                elif pos_text[c].pos_ == 'PRON':
                    actors = actors.union(prev_actors)
                elif pos_text[c].pos_ == 'VERB':
                    break
                c += 1
            for i in actors:
                if i.title() not in use_case:
                    use_case[i.title()] = set()
            if not actors and not flag:
                actors = prev_actors
            if flag:
                prev_actors = actors
            else:
                prev_actors = prev_actors.union(actors)
            flag = False
            if c >= len(pos_text) or pos_text[c].lemma_.lower() in ['include', 'involve', 'consist', 'contain', 'be']:
                c += 1
                continue
            v = pos_text[c]
            u = v.lemma_
            c += 1
            while c < len(pos_text):
                if (pos_text[c].pos_ == 'VERB' and pos_text[c].dep_ == 'conj') or (pos_text[c].pos_ == 'CCONJ' and pos_text[c] in v.children):
                    break
                if pos_text[c].dep_ == 'dobj':
                    u += " " + pos_text[c].lemma_
                c += 1
            for i in actors:
                use_case[i.title()].add(u)
    x = list(use_case.keys())
    for i in x:
        if not use_case[i]:
            del use_case[i]
    return use_case
                

def createUML(doc):

    use_case = knowledgeExtract(doc)
    fontsize = 15
    font = ImageFont.truetype("arial.ttf", fontsize)
    n = len(use_case.keys())
    cases = set()
    actors = list(use_case.keys())
    for actor in use_case:
        cases = cases.union(set(use_case[actor]))
    cases = list(cases)
    im = Image.new('RGB', (800, 700), (255, 255, 255))
    actor = Image.open(r'static\actor.jpg')
    draw = ImageDraw.Draw(im)
    half = n//2
    div1 = 700//(n-half)
    for i in range(n-half):
        im.paste(actor, (50+(50*(i%2)), div1*i+div1//2-50))
        draw.text((50+(50*(i%2)), div1*i+div1//2+100),actors[i],(0,0,0),font=font)
    div2 = 700//half
    for i in range(half):
        im.paste(actor, (700-(50*(i%2)), div2*i+div2//2-50))
        draw.text((700-(50*(i%2)), div2*i+div2//2+100),actors[n-half+i],(0,0,0),font=font)
    x = 700//len(cases)
    for i in range(len(cases)): 
        draw.ellipse((300, x*i+5, 500, x*(i+1)-5),fill=None, outline=(0, 0, 0))
        draw.text((325, x*(i+0.5)-10),cases[i].capitalize(),(0,0,0),font=font)
        for j in range(n-half):
            if cases[i] in use_case[actors[j]]:
                shape = [(125+(50*(j%2)), div1*j+div1//2+50),(300,x*(i+0.5))]
                draw.line(shape, fill =(0,0,0), width = 1)
        for j in range(half):
            if cases[i] in use_case[actors[n-half+j]]:
                shape = [(675-(50*(j%2)), div2*j+div2//2+50),(500,x*(i+0.5))]
                draw.line(shape, fill =(0,0,0), width = 1)
    im.save('static\pillow_imagedraw.jpg',quality=95)



