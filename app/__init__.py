from flask import Flask, render_template, send_file, redirect, request, jsonify
from config import app_config
from app.database import db_session
from app.models import CertificateTree, ResourceCertificate, Roa, Manifest, Crl
#from app.data_api import data_api
#from app.analysis_api import analysis_api
#from app.util import DateConverter


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    #app.url_map.converters['date'] = DateConverter
    #app.register_blueprint(data_api, url_prefix='/data')
    #app.register_blueprint(analysis_api, url_prefix='/analysis')

    @app.route('/')
    def show_index():
        cert_trees = db_session.query(CertificateTree).filter(CertificateTree.tree_name == "RIPE").all()
        return jsonify([r.asdict() for r in cert_trees])
        #return render_template('index.html')

    @app.route('/api/objects/rc/<cert_name>')
    def get_resource_certificate(cert_name):
        rc = db_session.query(ResourceCertificate).filter(ResourceCertificate.certificate_name == cert_name).first()
        return jsonify(rc.asdict())

    @app.route('/api/objects/mft/<mft_name>')
    def get_manifest(mft_name):
        rc = db_session.query(Manifest).filter(Manifest.manifest_name == mft_name).first()
        return jsonify(rc.asdict())

    @app.route('/api/objects/crl/<crl_name>')
    def get_crl(crl_name):
        rc = db_session.query(Crl).filter(Crl.crl_name == crl_name).first()
        return jsonify(rc.asdict())

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


