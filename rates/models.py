from gino import Gino

db = Gino()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    password_hash = db.Column(db.String())


class Currency(db.Model):
    __tablename__ = 'currency'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)


class Rate(db.Model):
    __tablename__ = 'rate'

    id = db.Column(db.Integer(), primary_key=True)
    currency_id = db.Column(db.Integer(), db.ForeignKey(Currency.id))
    date = db.Column(db.DateTime())
    rate = db.Column(db.Float())
    volume = db.Column(db.Float())
