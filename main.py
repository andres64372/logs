from flask import Flask,Response,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wqyapkqferhyuj:f686ecd5580bc075cd87749604c8f268edbec4a28bb90a1dde0dc2f597b68109@ec2-52-3-239-135.compute-1.amazonaws.com:5432/d1h0h0h3c59pd1'
db = SQLAlchemy(app)

class Logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.Text, nullable=False)
    typ = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False,default=datetime.datetime.now())

    def __repr__(self):
        return f"{self.env} - {self.date.strftime('%Y-%m-%d %H:%M')}"

@app.route('/',methods=['GET','POST','DELETE'])
def index():
    if request.method == 'GET':
        try:
            query = Logs.query.order_by(Logs.date.desc()).limit(100).all()
        except:
            return 'Failed to load db',500
        csv = ''
        for log in query:
            csv = csv + f"{log.env} -- {log.typ} -- {log.text} -- {log.date.strftime('%Y-%m-%d %H:%M')}\n"
        return Response(csv, mimetype="text/csv", headers={"Content-disposition":"attachment; filename=data.log"})
    
    if request.method == 'POST':
        data = request.get_json()
        if 'text' not in data.keys():
            return jsonify({'Success':False}),400
        env = data['env']
        text = data['text']
        typ = data['typ']
        try:
            db.session.add(Logs(env=env,text=text,typ=typ))
            db.session.commit()
        except:
            return jsonify({'Success':False}),500
        return jsonify({'Success':True}),200

    if request.method == 'DELETE':
        try:
            db.session.query(Logs).delete()
            db.session.commit()
        except:
            return 'Failed to load db',500
        return jsonify({'Success':True}),200

if __name__ == '__main__':
    app.run(port=5000)