from flask import Flask, render_template, send_file, redirect, request, jsonify
from config import app_config
from app.database import db_session
from app.models import CertificateTree, ResourceCertificate, Roa, Manifest, Crl
#from app.data_api import data_api
#from app.analysis_api import analysis_api
#from app.util import DateConverter

def jsonify_or_error(obj, obj_name):
    if obj:
        return jsonify(obj.asdict())
    else:
        return jsonify({'error':True, 'description': "File doesn't exist", 'filename': obj_name})


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    #app.url_map.converters['date'] = DateConverter
    #app.register_blueprint(data_api, url_prefix='/data')
    #app.register_blueprint(analysis_api, url_prefix='/analysis')

    @app.route('/')
    def show_index():
        return render_template('index.html')


    @app.route('/api/objects/meta/rc/children/<parent_id>')
    def get_rc_children_meta(parent_id):
        rc = db_session.query(ResourceCertificate).filter(ResourceCertificate.parent_id == parent_id).all()
        roas = db_session.query(Roa).filter(Roa.parent_id == parent_id).all()
        f = {'parent': parent_id, 'data': []}
        for c in rc:
            c = c.asdict()
            d = {'id': c['id'], 'value': c['certificate_name'], 'webix_kids': c['has_kids'], 'mft_name': c['manifest']}
            f['data'].append(d)
        for roa in roas:
            roa = roa.asdict()
            d = {'id': roa['id'], 'value': roa['roa_name'], 'webix_kids': False }
            f['data'].append(d)
        return jsonify(f)


    @app.route('/api/objects/meta/rc/<cert_name>')
    def get_resource_certificate_meta(cert_name):
        rc = db_session.query(ResourceCertificate).filter(ResourceCertificate.certificate_name == cert_name).first()
        rc = rc.asdict()
        d = {'id': rc['id'], 'value': rc['certificate_name'], 'webix_kids': rc['has_kids'], 'mft_name': rc['manifest']}
        return jsonify(d)


    @app.route('/api/objects/ct/<name>')
    def get_certificate_tree(name):
        cert_tree = db_session.query(CertificateTree).filter(CertificateTree.tree_name == name).first()
        return jsonify_or_error(cert_name, name)


    @app.route('/api/objects/ct/all')
    def get_certificate_trees():
        cert_trees = db_session.query(CertificateTree).all()
        return jsonify([r.asdict() for r in cert_trees])

    @app.route('/api/objects/rc/<cert_name>')
    def get_resource_certificate(cert_name):
        rc = db_session.query(ResourceCertificate).filter(ResourceCertificate.certificate_name == cert_name).first()
        return jsonify_or_error(rc, cert_name)

    @app.route('/api/objects/mft/<mft_name>')
    def get_manifest(mft_name):
        rc = db_session.query(Manifest).filter(Manifest.manifest_name == mft_name).first()
        return jsonify_or_error(rc, mft_name)

    @app.route('/api/objects/crl/<crl_name>')
    def get_crl(crl_name):
        rc = db_session.query(Crl).filter(Crl.crl_name == crl_name).first()
        return jsonify_or_error(rc, crl_name)

    @app.route('/api/objects/roa/<roa_name>')
    def get_roa(roa_name):
        rc = db_session.query(Roa).filter(Roa.roa_name == roa_name).first()
        return jsonify(rc.asdict())

    @app.route('/api/filter/', methods = ['POST'])
    def filter_objects():
        content = request.get_json()
        
        filter_attr = content['filter_attribute']
        filter_value = content['filter_value']
        file_type = content['file_type']
        cert_tree = content['tree_name']
    
        results = []
        
        if file_type == "cer" or file_type == "all":
            query = db_session.query(ResourceCertificate.id, ResourceCertificate.certificate_name).filter(ResourceCertificate.certificate_tree == cert_tree)
            if filter_attr == "filename":
                query = query.filter(ResourceCertificate.certificate_name.like("%"+filter_value+"%"))

            [results.append({'id':rc[0], 'value':rc[1]}) for rc in query.all()]
            return jsonify(results)

        return 'JSON posted\n'

        # "Certificate Tree: (tree_name")
        # "Parent object" : If null, only look at TA of cert_tree. if not null,
        # only look at children of that parent object
        # "File type: [.cer, .roa, or "both"]
        # validation status: [passed, warning, error] (has ot be at least one)
        # filename
        # location (not yet)
        # subject, issuer
        # Resource (IP, ASN, Ip prefix)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


