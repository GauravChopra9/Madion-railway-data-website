import pandas as pd
from flask import Flask, request, jsonify
import re
import time
import flask
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import io

app = Flask(__name__)
# df = pd.read_csv("main.csv")

counter = 0
count_A = 0
count_B = 0

@app.route('/')
def home():
    global counter
    global count_A
    global count_B
    if counter < 10:
        if counter % 2 == 0:
            with open("index_A.html") as f:
                counter = counter + 1
                html = f.read()
                return html

        else:
            with open("index_B.html") as f:
                counter = counter + 1
                html = f.read()
                return html
    else:
        if count_A > count_B:
            with open("index_A.html") as f:
                html = f.read()
                return html

        else:
            with open("index_B.html") as f:
                html = f.read()
                return html
        
        

@app.route('/browse.html')
def browse():
    # The csv file was gotten from kaggle
    df = pd.read_csv("main.csv")
    pd.set_option('display.max_rows', None)
    return '<h1>{}</h1> {}'.format("Lets start browsing!!", df._repr_html_())

@app.route('/donate.html')
def donate():
    global count_A
    global count_B
    
    if request.args.get("from") == "A":
        count_A = count_A + 1

    if request.args.get("from") == "B":
        count_B = count_B + 1
    
    with open("donate.html") as f:
        html = f.read()
    return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$", email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
            
        with open(r"emails.txt", "r") as t:
            num_subscribed = len(t.readlines())
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify(f"Entered an invalid email address") # 3



history = {}
@app.route('/browse.json')
def JSON():
    global history
    
    if time.time() - history.get(request.remote_addr, 0.0) < 60:
        return flask.Response("<b> go away <b>", status = 429, headers = {"Retry-After": "60"})
    
    else:
        history[request.remote_addr] = time.time()
        df = pd.read_csv("main.csv")
        return jsonify(df.to_dict("index"))
    
    
@app.route('/visitors.json')
def visitors():
    return jsonify(history)
    
@app.route('/dashboard_1.svg')
def fig1():
    fig, ax = plt.subplots(figsize=(15,4))
    
    df = pd.read_csv("main.csv")
    new_df = df[:10]
    
    plot_type = request.args.get("plot")
    if plot_type == None:
        new_df.plot.line("StopID", "Sunday", legend=False, ax=ax)
        ax.set_xlabel("StopID")
        ax.set_ylabel("Traffic on a sunday")
        plt.tight_layout()
    
    if plot_type == "bar":
        new_df.plot.bar("StopID", "Saturday", legend=False, ax=ax)
        ax.set_xlabel("StopID")
        ax.set_ylabel("Traffic on a saturday")
        plt.tight_layout()
    
    f = io.StringIO()
    fig.savefig(f, format = "svg")
    plt.close()
    return flask.Response(f.getvalue(), headers = {"Content-Type" : "image/svg+xml"}) 

@app.route('/dashboard_2.svg')
def fig3():
    fig, ax = plt.subplots(figsize=(15,4))
    ax.set_xlabel("StopDescription")
    ax.set_ylabel("IntersectionID")
    plt.tight_layout()
    
    df = pd.read_csv("main.csv")
    new_df = df[:10]
    new_df.plot.bar("StopID", "IntersectionID", legend=False, ax=ax)
    
    
    f = io.StringIO()
    fig.savefig(f, format = "svg")
    plt.close()
    return flask.Response(f.getvalue(), headers = {"Content-Type" : "image/svg+xml"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False)
