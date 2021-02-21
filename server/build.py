from app import db

if __name__ == '__main__':
    from model import *
    db.drop_all()
    db.create_all()
    camera = Camera(name='Raspberry Pi3')
    db.session.add(camera)
    db.session.commit()
    print(camera.id)
