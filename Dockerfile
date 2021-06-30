#元のイメージの指定(軽量なもので、バージョン指定できるものを選んだ)
FROM python:3.9.6-slim

WORKDIR /app

#ローカルのファイルをappにすべて読み込んでいる
COPY . /app

#環境構築
RUN apt-get update
RUN apt-get install -y software-properties-common

# python環境
RUN pip install -r requirements.txt

# R環境構築
# RUN apt-get -y install r-base r-base-dev
RUN apt install -y gnupg
# RUN apt-key adv --keyserver keys.gnupg.net --recv-key 'E19F5F87128899B192B1A2C2AD5F960A256A04AF'
RUN apt-key add jranke.asc
RUN add-apt-repository "deb http://cloud.r-project.org/bin/linux/debian buster-cran40/"
RUN apt-get update
RUN apt install -y r-base
RUN apt-get install -y libgmp3-dev
RUN Rscript R_requirements.r

# flaskサーバの起動
CMD ["python", "app.py"]

# imageのビルド
# docker image build -t [image_name] .

# コンテナ作成
# docker run -p 5000:5000 -v ${PWD}:/app --name [container_name] [image_name]
# 注意 ${PWD}:/appの部分 →コンテナ内のソースと同じ内容がローカルにある前提になっている
#      ローカルの変更をすぐに反映できるように、依存関係ができている
#  bin などの不要なファイルも読んでいるかもしれないので、できればbuildするものだけにしたい
# 