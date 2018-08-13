from flask import Flask, render_template, send_file, redirect, request, jsonify
from config import app_config
from app.database import db_session
from app.models import CertificateTree, ResourceCertificate, Roa, Manifest, Crl
from sqlalchemy.sql import operators
from IPy import IP
#from app.data_api import data_api
#from app.analysis_api import analysis_api
#from app.util import DateConverter

def jsonify_or_error(obj, obj_name):
    if obj:
        return jsonify(obj.asdict())
    else:
        return jsonify({'error':True, 'description': "File doesn't exist", 'filename': obj_name})

def is_asn(value):
    try:
        asn = int(value)
        return True
    except ValueError:
        return False

def is_ip(value):
    try:
        ip = IP(value)
        return True
    except ValueError:
        return False



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
            d = {'id': c['id'], 'value': c['certificate_name'], 'webix_kids': c['has_kids'], 'mft_name': c['manifest'], 'crl_name': c['crl']}
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
        d = {'id': rc['id'], 'value': rc['certificate_name'], 'webix_kids': rc['has_kids'], 'mft_name': rc['manifest'], 'crl_name': rc['crl']}
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
            query = db_session.query(ResourceCertificate.id, ResourceCertificate.certificate_name, ResourceCertificate.manifest, ResourceCertificate.crl).filter(ResourceCertificate.certificate_tree == cert_tree)
            if filter_attr == "filename":
                query = query.filter(ResourceCertificate.certificate_name.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3]}) for rc in query]
            elif filter_attr == "subject":
                query = query.filter(ResourceCertificate.subject.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3]}) for rc in query]
            elif filter_attr == "issuer":
                query = query.filter(ResourceCertificate.issuer.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3]}) for rc in query]
            elif filter_attr == "serial_nr":
                query = query.filter(ResourceCertificate.serial_nr == int(filter_value))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3]}) for rc in query]
            elif filter_attr == "resource":
                if is_asn(filter_value):
                    asn = int(filter_value)
                    sql_query = "select id, certificate_name, manifest, crl from resource_certificate where (({0}::int8 <@ ANY (asn_ranges) OR {0} =ANY(asns)) AND certificate_tree='{1}');".format(asn, cert_tree)
                    query = db_session.execute(sql_query)
                    [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3]}) for rc in query]
                elif is_ip(filter_value):
                    sql_query = "select id, certificate_name, manifest, crl from resource_certificate where ('{0}'::inet <<= ANY (prefixes) AND certificate_tree='{1}');".format(filter_value, cert_tree)
                    query = db_session.execute(sql_query)
                    [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3]}) for rc in query]

        if file_type == "roa" or file_type == "all":
            query = db_session.query(Roa.id, Roa.roa_name).filter(Roa.certificate_tree == cert_tree)
            if filter_attr == "filename":
                query = query.filter(Roa.roa_name.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1]}) for rc in query.all()]
            elif filter_attr == "subject":
                query = query.filter(Roa.roa_name.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1]}) for rc in query.all()]
            elif filter_attr == "issuer":
                query = query.filter(Roa.roa_name.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1]}) for rc in query.all()]
            elif filter_attr == "serial_nr":
                query = query.filter(Roa.roa_name == "WAT")
                [results.append({'id':rc[0], 'value':rc[1]}) for rc in query.all()]
            elif filter_attr == "resource":
                if is_asn(filter_value):
                    asn = int(filter_value)
                    query = query.filter(Roa.asn == asn)
                    [results.append({'id':rc[0], 'value':rc[1]}) for rc in query.all()]
                elif is_ip(filter_value):
                    sql_query = "SELECT id, roa_name FROM roa WHERE '{0}'::inet <@ ANY (prefixes) AND certificate_tree='{1}';".format(filter_value, cert_tree)
                    print(sql_query)
                    query = db_session.execute(sql_query)
                    [results.append({'id':rc[0], 'value':rc[1]}) for rc in query]
        return jsonify(results)


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


