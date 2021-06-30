from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
# from random import random
import pyper as pr
import pandas as pd
import uuid
import sys,os



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
        sys.stderr.write(f"args: {args}\n")

        # 因子の名前リストを作る
        def getFactorsAndLevels(args):
            """
            request.form から、キーが一致する値を取り出して
            factorsとlevelsのリストとして返す
            ●出力の形式
            factors = ["因子1_名前","因子２_名前", "因子３_名前"]
            levels = [[因子１_水準１,因子1_水準2,..],[..],[因子１_水準１,因子1_水準2,..]]

            """
            n = 3 # 因子数の設定値
            # sys.stderr.write(str(args))

            # factors作成
            # argsにあるfactorに入力された値をリストにする
            factors = []
            factors_key_list = [ f'factor{i}_label' for i in range(1, 1 + n, 1)]
            for factor_key in factors_key_list:
                factors += args.get(factor_key)
            # print(factors)

            # levels作成
            # levelsに入力された値を、コンマ区切りで切って要素を取得する
            levels = []
            levels_key_list = [ f'factor{i}_lvs' for i in range(1, 1 + n, 1)]

            for level_key in levels_key_list:
                sys.stderr.write(str(args.get(level_key)))
                levels.append(args.get(level_key).split(",")) #Flaskサーバで直接レスポンスを受け取る場合、文字列がリストに入ってくるので、index指定の[0]が必要(HerokuやDockerのほうに合わせている)            # sys.stderr.write(f"levels: {levels}\n")
            return factors, levels
        
        def makeOaDesign(factors, levels):
            """
            factorsとlevelsのリストをRに渡して、OaDesignを作って、データフレームとして返す関数
            TODO: PypeR意外の選択肢を探したい(Rからのレスポンスが無い場合、pythonのプロセスが停止しない)
                    デバックなども考えると、エラーメッセージが出るものがいい
            """
            # STEP１：R にわたすリストと値を作る
            # factorのlabel数と水準数別
            # sys.stderr.write(f"levels: {levels}")
            nlevels = [ len(lvs) for lvs in levels ]

            # STEP2: R内で計画を作成する
            r = pr.R()
            r.assign("nlevels", nlevels)
            sys.stderr.write(f"nlevels: {nlevels}")
            r('library("DoE.base")')
            r("print(length(nlevels))")
            r("table = oa.design(nfactors = length(nlevels), nlevels = nlevels)")

            # STEP3: Rから計画を出力する
            oa_design = pd.DataFrame(r.get("table"))

            #値の置換処理
            ## 後からリファクタしやすいように関数化するnle
            def makeValueMap(levels):
                """
                arrayの値と元の入力値との対応を返す
                入力 各水準の入力値が入った2重のリスト
                出力 arrayの値がキー、元の入力値が値の辞書が入ったリスト
                """
                replace_levels = []
                
                for level in levels:
                    # arrayの中と同じオブジェクトを生成する
                    rep_key = [str_v.encode() for str_v in [str(v) for v in range(1,len(level)+1)]] #1始まり
                    #対応関係の辞書
                    value_map = dict(zip(rep_key, level))
                    replace_levels.append(value_map)
                    
                return replace_levels


            #出力用df
            new_oa_design = pd.DataFrame({"Exp No.": range(1,len(oa_design)+1)})

            # 置換処理
            ## 列名の置換
            rep_col = dict(zip(oa_design.columns, factors))
            oa_design = oa_design.rename(columns=rep_col)
            
            ## 値の置換
            replace_levels = makeValueMap(levels)
            
            for col, replace_vals in zip(oa_design.columns, replace_levels):
                sr_repl = oa_design[col].replace(replace_vals)
                new_oa_design = pd.concat([new_oa_design,sr_repl], axis=1)
                
            return new_oa_design

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
            table = oa_design.to_html(classes=["table", "table-bordered", "table-hover"], index=False)
            page_html = html_template.format(table=table)

            return page_html

        #ここらから直交表をつくる
        factors, levels = getFactorsAndLevels(args)
        oa_design = makeOaDesign(factors,levels)
        
        sys.stderr.write(f"Oa_Design size: {oa_design.shape}\n")

        res = makeResponse(oa_design)
        return res



if __name__ == "__main__":
    #herokuで動作するために追加
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port,debug=True)