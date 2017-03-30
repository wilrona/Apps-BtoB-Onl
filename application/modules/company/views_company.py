__author__ = 'User'


from ...modules import *
from models_company import Company, Config_reference
from forms_company import FormCompany

prefix = Blueprint('company', __name__)


@prefix.route('/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'entreprise')])
def view():

    title_parent = 'Configuration'
    title_page = 'Information de l\'entreprise'


    company = Company.objects().first()

    form = FormCompany(obj=company)

    if form.validate_on_submit() and request.method == 'POST':

        company = Company.objects().first()
        company.name = form.name.data
        company.bp = form.bp.data
        company.adress = form.adress.data
        company.ville = form.ville.data
        company.pays = form.pays.data
        company.phone = form.phone.data
        company.capital = form.capital.data
        company.numcontr = form.numcontr.data
        company.registcom = form.registcom.data
        company.email = form.email.data
        company.siteweb = form.siteweb.data
        company.slogan = form.slogan.data
        company.typEnt = form.typEnt.data
        company.facebook = form.facebook.data
        company.twitter = form.twitter.data
        company.quartier = form.quartier.data
        company.save()


        flash('Enregistrement reussie avec success', 'success')
        return redirect(url_for('company.view'))

    return render_template('company/view.html', **locals())



prefix_param = Blueprint('parametrage', __name__)


@prefix_param.route('/', methods=['POST', 'GET'])
@login_required
@roles_required([('super_admin', 'general')])
def view():

    title_page = 'Reference Generale'

    data = Config_reference.objects().first()

    if not data:
        data = Config_reference()

    if request.method == 'POST' and request.form:

        ref_fact = request.form['ref_fact']
        if request.form['ref_fact']:
            data.ref_fact = ref_fact

        ref_devis = request.form['ref_devis']
        if request.form['ref_devis']:
            data.ref_devis = ref_devis

        ref_site = request.form['ref_site']
        if request.form['ref_site']:
            data.ref_site = ref_site

        tva = float(request.form['taux_tva'])
        if request.form['taux_tva']:
            data.taux_tva = tva

        email = request.form['email_service']
        if request.form['email_service']:
            data.email_service = email

        min = request.form['min_pass_by_ecran']
        if request.form['min_pass_by_ecran']:
            data.min_pass_by_ecran = min

        data.save()

        return redirect(url_for('parametrage.view'))

    return render_template('company/setting.html', **locals())