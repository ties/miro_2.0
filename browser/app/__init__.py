from flask import Flask, render_template, send_file, redirect, request, jsonify, Response
from config import app_config
from app.database import db_session
from app.models import CertificateTree, ResourceCertificate, Roa, Manifest, Crl, Stats, RoaResourceCertificate
from sqlalchemy.sql import operators
from IPy import IP
import json
import os.path
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
            d = {'id': c['id'], 'value': c['certificate_name'], 'webix_kids': c['has_kids'], 'mft_name': c['manifest'], 'crl_name': c['crl'], 'icon':c['validation_status'].lower()}
            f['data'].append(d)
        for roa in roas:
            roa = roa.asdict()
            d = {'id': roa['id'], 'value': roa['roa_name'], 'webix_kids': False, 'icon':roa['validation_status'].lower() }
            f['data'].append(d)
        return jsonify(f)


    @app.route('/api/objects/meta/rc/<cert_name>')
    def get_resource_certificate_meta(cert_name):
        rc = db_session.query(ResourceCertificate).filter(ResourceCertificate.certificate_name == cert_name).first()
        rc = rc.asdict()
        d = {'id': rc['id'], 'value': rc['certificate_name'], 'webix_kids': rc['has_kids'], 'mft_name': rc['manifest'], 'crl_name': rc['crl'],  'icon':rc['validation_status'].lower()}
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
    
    @app.route('/api/stats/all')
    def get_stats():
        stats = db_session.query(Stats).all()
        return jsonify([r.asdict() for r in stats])

    @app.route('/api/objects/crl/<crl_name>')
    def get_crl(crl_name):
        rc = db_session.query(Crl).filter(Crl.crl_name == crl_name).first()
        return jsonify_or_error(rc, crl_name)

    @app.route('/api/objects/roa/<roa_name>')
    def get_roa(roa_name):
        rc = db_session.query(Roa).filter(Roa.roa_name == roa_name).first()
        return jsonify(rc.asdict())

    @app.route('/api/objects/roa_rc/<roa_name>')
    def get_roa_rc(roa_name):
        rc = db_session.query(RoaResourceCertificate).filter(RoaResourceCertificate.roa_container == roa_name).first()
        return jsonify(rc.asdict())

    @app.route('/api/tree/<tree_name>', methods=['GET'])
    def download_json_tree(tree_name):
        path = app.config['JSON_CERTIFICATE_TREE_FILES'] + '/' + tree_name
        try:
            content = str(json.load(open(path, 'r')))
        except:
            content = {"error": "File not found"}
        return Response(content, mimetype='application/json',
                headers={'Content-Disposition':'attachment;filename='+tree_name})

    @app.route('/api/filter/', methods = ['POST'])
    def filter_objects():
        content = request.get_json()
        
        filter_attr = content['filter_attribute']
        filter_value = content['filter_value']
        file_type = content['file_type']
        cert_tree = content['tree_name']
        incl_valids = content['include_valids']
        incl_warnings = content['include_warnings']
        incl_errors = content['include_errors']
        results = []
        print(content)
        
        if file_type == "cer" or file_type == "all":
            query = db_session.query(ResourceCertificate.id, ResourceCertificate.certificate_name, ResourceCertificate.manifest, ResourceCertificate.crl, ResourceCertificate.validation_status).filter(ResourceCertificate.certificate_tree == cert_tree)
            # If all are 1, we don't need a filter. If not we have to filter a
            # subset
            if not (incl_valids and incl_warnings and incl_errors):
                if not incl_valids:
                    query = query.filter(ResourceCertificate.is_valid == False)
                if not incl_warnings:
                    query = query.filter(ResourceCertificate.validation_warnings == None)
                if not incl_errors:
                    query = query.filter(ResourceCertificate.validation_errors == None)

            if filter_attr == "filename":
                query = query.filter(ResourceCertificate.certificate_name.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]
            elif filter_attr == "subject":
                query = query.filter(ResourceCertificate.subject.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]
            elif filter_attr == "issuer":
                query = query.filter(ResourceCertificate.issuer.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]
            elif filter_attr == "serial_nr":
                query = query.filter(ResourceCertificate.serial_nr == int(filter_value))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]
            elif filter_attr == "location":
                query = query.filter(ResourceCertificate.location.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]
            elif filter_attr == "resource":
                if is_asn(filter_value):
                    asn = int(filter_value)
                    sql_query = "SELECT id, certificate_name, manifest, crl, validation_status FROM resource_certificate WHERE "
                    sql_query += "("
                    sql_query += "({0}::int8 <@ ANY (asn_ranges) OR {0} =ANY(asns)) ".format(asn)
                    sql_query += "AND certificate_tree='{0}' ".format(cert_tree)

                    if not (incl_valids and incl_warnings and incl_errors):
                        if not incl_valids:
                            sql_query += "AND is_valid = false "
                        if not incl_warnings:
                            sql_query += "AND validation_warnings = NULL "
                        if not incl_errors:
                            sql_query += "AND validation_errors = NULL "


                    sql_query += ");"
                    query = db_session.execute(sql_query)
                    [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]
                elif is_ip(filter_value):
                    sql_query = "SELECT id, certificate_name, manifest, crl, validation_status FROM resource_certificate WHERE "
                    sql_query += "("
                    sql_query += "'{0}'::inet <<= ANY (prefixes) ".format(filter_value)
                    sql_query +=  "AND certificate_tree='{0}' ".format(cert_tree)
                    if not (incl_valids and incl_warnings and incl_errors):
                        if not incl_valids:
                            sql_query += "AND is_valid = false "
                        if not incl_warnings:
                            sql_query += "AND validation_warnings = NULL "
                        if not incl_error:
                            sql_query += "AND validation_errors = NULL "
                    sql_query += ");"
                    query = db_session.execute(sql_query)
                    [results.append({'id':rc[0], 'value':rc[1], 'mft_name':rc[2], 'crl_name':rc[3], 'icon':rc[4].lower()}) for rc in query]

        if file_type == "roa" or file_type == "all":
            query = db_session.query(Roa.id, Roa.roa_name, Roa.validation_status).filter(Roa.certificate_tree == cert_tree)
            if filter_attr == "filename":
                query = query.filter(Roa.roa_name.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query.all()]
            elif filter_attr == "subject":
                query = db_session.query(RoaResourceCertificate.parent_id, RoaResourceCertificate.roa_container).filter(RoaResourceCertificate.certificate_tree == cert_tree)
                query = query.filter(RoaResourceCertificate.subject.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query.all()]
            elif filter_attr == "issuer":
                query = db_session.query(RoaResourceCertificate.parent_id, RoaResourceCertificate.roa_container).filter(RoaResourceCertificate.certificate_tree == cert_tree)
                query = query.filter(RoaResourceCertificate.issuer.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query.all()]
            elif filter_attr == "serial_nr":
                query = db_session.query(RoaResourceCertificate.parent_id, RoaResourceCertificate.roa_container).filter(RoaResourceCertificate.certificate_tree == cert_tree)
                query = query.filter(RoaResourceCertificate.serial_nr == int(filter_value))
                [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query.all()]
            elif filter_attr == "location":
                query = query.filter(Roa.location.like("%"+filter_value+"%"))
                [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query.all()]

            elif filter_attr == "resource":
                if is_asn(filter_value):
                    asn = int(filter_value)
                    query = query.filter(Roa.asn == asn)
                    [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query.all()]
                elif is_ip(filter_value):
                    sql_query = "SELECT id, roa_name, validation_status FROM roa WHERE "
                    sql_query += "("
                    sql_query += "'{0}'::inet <@ ANY (prefixes) ".format(filter_value)
                    sql_query += "AND certificate_tree='{0}' ".format(cert_tree)
                    if not (incl_valids and incl_warnings and incl_errors):
                        if not incl_valids:
                            sql_query += "AND is_valid = false "
                        if not incl_warnings:
                            sql_query += "AND validation_warnings = NULL "
                        if not incl_errors:
                            sql_query += "AND validation_errors = NULL "
                    sql_query += ");"
                    query = db_session.execute(sql_query)
                    [results.append({'id':rc[0], 'value':rc[1], 'icon':rc[2].lower()}) for rc in query]
        return jsonify(results)


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


