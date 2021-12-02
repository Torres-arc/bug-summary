import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)  # 在该模块中Flask标识，可以传入任意字符串
# manager = Manager(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/list_mon', methods=['GET'])
def list_mon():
    mon_list = os.listdir('db')
    print(mon_list)
    try:
        return {"month": mon_list}, 200, {"ContentType": "application/json", 'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        print(e)
        return jsonify({"code": "异常", "message": "{}".format(e)})


@app.route('/get_data', methods=['GET'])
def list_data():
    month = request.args.get('month')
    path = os.listdir('db/%s' % month)
    new_js = {}
    try:
        for pbi in path:
            with open('pbi.json', 'r', encoding='utf-8') as msg_file:
                msg = json.load(msg_file)
                target = msg[month][(pbi.split('.'))[0]]
                msg_file.close()
            with open('db/%s/%s' % (month, pbi), 'r', encoding='utf-8') as f:
                state = json.load(f)
                pbi_id = (pbi.split('.'))[0]
                keys = target+'---'+str(pbi_id)
                new_js[keys] = []
                for i, j in state.items():
                    for x, y in j.items():
                        new_js[keys].append({"level": i, "date": x, "value": y})
                    f.close()
        return new_js, 200, {"ContentType": "application/json", 'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        print(e)
        return jsonify({"code": "异常", "message": "{}".format(e)})


# @app.route('/get_msg', methods=['GET'])
# def get_msg():
#     pbi = request.args.get('pbi')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    # path = os.listdir('db')
    # print(path)