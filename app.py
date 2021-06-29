from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
# from random import random
import pyper as pr
import pandas as pd
import uuid
import sys



app = Flask(__name__)

@app.route('/',  methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/oa_design',  methods=['GET', 'POST'])
def oa_design():
    if request.method == 'GET':
        print("GET")
        return render_template("oa_design.html")

    elif request.method == 'POST':
        # print(request.form)
        # test = request.form
        args = dict(request.form)
        print(f"args:{args}")

        # 因子の名前リストを作る
        def getLabelsAndLevels(args):
            """
            request.form から、キーが一致する値を取り出して
            labelsとlevelsのリストとして返す
            ●出力の形式
            labels = ["因子1_名前","因子２_名前", "因子３_名前"]
            levels = [[因子１_水準１,因子1_水準2,..],[..],[因子１_水準１,因子1_水準2,..]]

            """
            n = 3 # 因子数の設定値

            # labels作成
            labels = []
            labels_key_list = [ f'factor{i}_label' for i in range(1, 1 + n, 1)]
            for label_key in labels_key_list:
                labels += args.get(label_key)
            # print(labels)

            # levels作成
            levels = []
            levels_key_list = [ f'factor{i}_lvs' for i in range(1, 1 + n, 1)]
            for level_key in levels_key_list:
                levels.append(args.get(level_key)[0].split(","))
            # print(levels)
            return labels, levels
        
        def makeOaDesign(labels, levels):
            """
            labelsとlevelsのリストをRに渡して、OaDesignを作って、データフレームとして返す関数
            TODO: 列の名前と値を、入力されたものに置換すること
            """
            # STEP１：R にわたすリストと値を作る
            # factorのlabel数と水準数別
            nlevels = [ len(lvs) for lvs in levels ]

            # STEP2: R内で計画を作成する
            r = pr.R()
            r.assign("nlevels", nlevels)
            r('library("DoE.base")')
            r("table = oa.design(nfactors = length(nlevels), nlevels = nlevels)")

            # STEP3: Rから計画を出力する
            oa_design = pd.DataFrame(r.get("table"))

            #この辺で置換処理を。。。

            return oa_design

        def makeViewFile(oa_design, file_name):
            """
            データフレーム(oa_design)をテーブルとして持ったhtmlファイルを作成する
            """
            # お試し用でコピペした https://qiita.com/nshinya/items/a46ef0002284d2f77789
            html_template = """
                <!doctype html>
                <html lang="ja">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
                </head>
                <body>
                    <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>
                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
                    <div class="container">
                        {table}
                    </div>
                </body>
                </html>
                """
            table = oa_design.to_html(classes=["table", "table-bordered", "table-hover"])
            html = html_template.format(table=table)

            with open(file_name, "w") as f:
                f.write(html)

        def makeResponse(oa_design):
            """
            データフレーム(oa_design)をテーブルとして持ったhtmlを作成する
            """
            # お試し用でコピペした https://qiita.com/nshinya/items/a46ef0002284d2f77789
            html_template = """
                <!doctype html>
                <html lang="ja">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
                </head>
                <body>
                    <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>
                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
                    <div class="container">
                        {table}
                    </div>
                </body>
                </html>
                """
            table = oa_design.to_html(classes=["table", "table-bordered", "table-hover"])
            page_html = html_template.format(table=table)

            return page_html

        #ここらから直交表をつくる
        labels, levels = getLabelsAndLevels(args)
        oa_design = makeOaDesign(labels,levels)
        
        sys.stderr.write(f"array size: {oa_design.shape}")

        res = makeResponse(oa_design)
        return res

        # ファイル化しない(本仕様)



if __name__ == "__main__":
    app.run(debug=True)