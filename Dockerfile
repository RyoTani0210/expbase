FROM python:3.9.6-slim
# とりあえず軽量なものかつバージョン指定できるものを選ぶ

WORKDIR /app

COPY . /app
#ローカルのファイルをappにすべて読み込んでいる

RUN pip install -r requirements.txt


CMD ["python", "app.py"]

# imageのビルド
# docker image build -t [image_name] .

#run
# docker run -p 5000:5000 -v ${PWD}:/app --name [container_name] [image_name]
# 注意 ローカルの変更をすぐに反映できるように、依存関係ができている
#  bin などの不要なファイルも読んでいるので、できればbuildするものだけにしたい
# 