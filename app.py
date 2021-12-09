from flask import Flask, render_template, redirect, request, url_for
import UseCase

app = Flask(__name__)

show = [0]*6
result = [[] for i in range(5)]
doc = ""

@app.route('/')
def check():
    return render_template("index.html", show = show, result = result, doc = doc)

@app.route('/submit',methods = ['POST'])
def submit_data():
    global show, result, doc
    if request.method == 'POST':
        print(request.form)
        doc = request.form['Text Acquisition']
        if request.form['action'] == 'Text Segmentation':
            show[0] = 1
            result[0] = UseCase.segmentation(doc)
        elif request.form['action'] == 'Text Tokenisation':
            show[1] = 1
            result[1] = UseCase.tokenization(doc)
        elif request.form['action'] == 'Pos Tagging':
            show[2] = 1
            result[2] = UseCase.posTag(doc)
        elif request.form['action'] == 'Port Lemmatization':
            show[3] = 1
            result[3] = UseCase.lemmatization(doc)
        elif request.form['action'] == 'Knowledge Extract':
            show[4] = 1
            result[4] = UseCase.knowledgeExtract(doc)
        elif request.form['action'] == 'Generate UML':
            show[5] = 1
            UseCase.createUML(doc)
        elif request.form['action'] == 'RESET':
            show = [0]*6
            result = [[] for i in range(5)]
            doc = ""
            return redirect(url_for('check'))
    # print(doc)
    return render_template("index.html", show = show, result = result, doc = doc)

if __name__ == '__main__':
    app.run(debug = True)

