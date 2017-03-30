__author__ = 'User'


from form_opportunite import FormOpportunite, FormRelance
from models_opportunite import Opportunite, Etape, Suivie, Activite, Libelle_Opportunite
from ..compagnie.forms_compagnie import FormClient
from ..company.models_company import Config_reference
from ..document.models_doc import Document
from ..site.models_site import Secteur
from ..user.forms_user import FormUser
from ...modules import *
from ..workflow import ckeck_etape

prefix_opportunite = Blueprint('opportunite', __name__)


@prefix_opportunite.route('/')
@login_required
def index():

    title_page = 'Opportunites'

    if current_user.has_roles([('super_admin', 'opportunite')]):
        datas = Opportunite.objects()
    else:
        datas = Opportunite.objects(vendeur_id=current_user.id)

    return render_template('opportunite/index.html', **locals())


@prefix_opportunite.route('/view/<objectid:opportunite_id>')
@login_required
def view(opportunite_id):

    title_page = 'Opportunites'

    data = Opportunite.objects.get(id=opportunite_id)

    if not current_user.has_roles([('super_admin', 'opportunite')]) and data.vendeur_id.id != current_user.id:
        return redirect(url_for('opportunite.index'))

    form = FormOpportunite(obj=data)

    customer = Client.objects.get(id=data.client_id.id)
    form_client = FormClient(prefix="client", obj=customer)
    if customer.secteur_id:
        form_client.secteur_id.data = str(customer.secteur_id.id)

    contact = Users.objects.get(id=data.contact_id.id)
    form_contact = FormUser(obj=contact)

    if contact.civilite:
        form_contact.civilite.data = str(contact.civilite.id)
    form.vendeur_id.data = str(data.vendeur_id.id)

    form_client.id.data = str(customer.id)
    form.id.data = str(opportunite_id)

    all = Users.objects(Q(user=True) & Q(is_enabled=True))
    form.vendeur_id.choices = [('', ' ')]
    for choice in all:
        form.vendeur_id.choices.append((str(choice.id), choice.first_name+' '+choice.last_name))

    all = Civilite.objects(actif=True)
    form_contact.civilite.choices = [('', ' ')]
    for choice in all:
        form_contact.civilite.choices.append((str(choice.id), choice.name))

    all = Secteur.objects(actif=True)
    form_client.secteur_id.choices = [('', ' ')]
    for choice in all:
        form_client.secteur_id.choices.append((str(choice.id), choice.name))

    etape_list = Etape.objects(actif=True).order_by('order')

    last_etape = Etape.objects(actif=True).order_by('-order').first()

    client_list = Client.objects(Q(client=True) & Q(actif=True))

    devis_count = Document.objects(Q(opportunite_id=data) & Q(devisDoc=True)).count()

    return render_template('opportunite/view.html', **locals())


@prefix_opportunite.route('/edit/<objectid:opportunite_id>', methods=['GET', 'POST'])
@prefix_opportunite.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit(opportunite_id=None):

    title_page = 'Opportunites'

    if opportunite_id:
        data = Opportunite.objects.get(id=opportunite_id)

        if data.status == global_etape[3]:
            return redirect(url_for('opportunite.view', opportunite_id=opportunite_id))

        if not current_user.has_roles([('super_admin', 'opportunite')], ['edit']) and data.vendeur_id.id != current_user.id:
            return redirect(url_for('opportunite.view', opportunite_id=opportunite_id))

        form = FormOpportunite(obj=data)

        customer = Client.objects.get(id=data.client_id.id)
        form_client = FormClient(prefix="client", obj=customer)
        if customer.secteur_id:
            form_client.secteur_id.data = str(customer.secteur_id.id)

        contact = Users.objects.get(id=data.contact_id.id)
        form_contact = FormUser(obj=contact)

        if contact.civilite:
            form_contact.civilite.data = str(contact.civilite.id)
        form.vendeur_id.data = str(data.vendeur_id.id)

        form_client.id.data = str(customer.id)
        form.id.data = str(opportunite_id)

        devis_count = Document.objects(Q(opportunite_id=data) & Q(devisDoc=True)).count()
    else:
        data = Opportunite()
        form = FormOpportunite()

        customer = Client()
        form_client = FormClient(prefix="client")

        contact = Users()
        form_contact = FormUser()

        if request.method == 'GET':
            form.vendeur_id.data = str(current_user.id)

        if 'client_exist' in request.form and request.form['client_exist']:
            form_client.id.data = request.form['client_exist']

    current_client = None
    contact_list = []
    if request.method == 'POST' and 'client_exist' in request.form and request.form['client_exist']:

        current_client = Client.objects.get(id=request.form['client_exist'])

        form_client.name.data = current_client.name
        form_client.email.data = current_client.email
        form_client.adress.data = current_client.adress
        form_client.bp.data = current_client.bp
        form_client.numcontr.data = current_client.numcontr
        form_client.raison.data = current_client.raison
        form_client.phone.data = current_client.phone
        form_client.rue.data = current_client.rue
        form_client.registcom.data = current_client.registcom
        form_client.ville.data = current_client.ville
        form_client.quartier.data = current_client.quartier
        form_client.urlsite.data = current_client.urlsite
        form_client.secteur_id.data = str(current_client.secteur_id.id)

        contact_list = [contact.user_id for contact in current_client.contact]

    current_contact = None
    if request.method == 'POST' and 'contact_exist' in request.form and request.form['contact_exist']:

        current_contact = Users.objects.get(id=request.form['contact_exist'])

        if current_contact.civilite:
            form_contact.civilite.data = str(current_contact.civilite.id)
        form_contact.id.data = current_contact.id
        form_contact.email.data = current_contact.email
        form_contact.first_name.data = current_contact.first_name
        form_contact.last_name.data = current_contact.last_name
        form_contact.fonction.data = current_contact.fonction
        form_contact.mobile.data = current_contact.mobile
        form_contact.telephone.data = current_contact.telephone

    from ..user.models_user import Roles
    admin_role = Roles.objects(valeur='super_admin').first()

    all = Users.objects(Q(user=True) & Q(is_enabled=True) & Q(roles__role_id__ne=admin_role))
    form.vendeur_id.choices = [('', ' ')]
    for choice in all:
        form.vendeur_id.choices.append((str(choice.id), choice.first_name+' '+choice.last_name))

    all = Civilite.objects(actif=True)
    form_contact.civilite.choices = [('', ' ')]
    for choice in all:
        form_contact.civilite.choices.append((str(choice.id), choice.name))

    all = Secteur.objects(actif=True)
    form_client.secteur_id.choices = [('', ' ')]
    for choice in all:
        form_client.secteur_id.choices.append((str(choice.id), choice.name))

    etape_list = Etape.objects(actif=True).order_by('order')
    client_list = Client.objects(Q(client=True) & Q(actif=True))

    libelle = []
    if not opportunite_id:
        libelle = Libelle_Opportunite.objects(actif=True)

    if form.validate_on_submit() and form_client.validate_on_submit() and form_contact.validate_on_submit():

        if not opportunite_id:
            data.name = form.name.data



        if data.vendeur_id and data.vendeur_id.id != current_user.id:
            vendeur = Users.objects(Q(id=form.vendeur_id.data) & Q(roles__role_id__ne=admin_role)).get()
            data.vendeur_id = vendeur
        else:
            vendeur = Users.objects.get(Q(id=current_user.id) & Q(roles__role_id__ne=admin_role)).get()
            data.vendeur_id = vendeur

        data.note = form.note.data

        if 'client_exist' in request.form and request.form['client_exist']:
            data.client_id = current_client
        else:
            if not opportunite_id:
                customer.name = form_client.name.data
                customer.email = form_client.email.data
                customer.adress = form_client.adress.data
                customer.bp = form_client.bp.data
                customer.client = True
                customer.numcontr = form_client.numcontr.data
                customer.actif = True
                customer.raison = form_client.raison.data
                customer.phone = form_client.phone.data
                customer.rue = form_client.rue.data
                customer.registcom = form_client.registcom.data
                customer.ville = form_client.ville.data
                customer.quartier = form_client.quartier.data
                customer.urlsite = form_client.urlsite.data

                secteur = Secteur.objects().get(id=form_client.secteur_id.data)
                customer.secteur_id = secteur

                the_contact = CompagniUser()
                the_contact.user_id = contact

                customer.contact.append(the_contact)
                customer = customer.save()

                data.client_id = customer

        if 'contact_exist' in request.form and request.form['contact_exist']:
            data.contact_id = current_contact
            data.etape = global_etape[0]
        else:
            if not opportunite_id:

                if form_contact.civilite.data:
                    civil = Civilite.objects.get(id=form_contact.civilite.data)
                    contact.civilite = civil
                contact.email = form_contact.email.data
                contact.first_name = form_contact.first_name.data
                contact.last_name = form_contact.last_name.data
                if form_contact.fonction.data:
                    contact.fonction = form_contact.fonction.data
                contact.mobile = form_contact.mobile.data
                contact.telephone = form_contact.telephone.data
                contact = contact.save()

                data.contact_id = contact
                data.etape = global_etape[0]

                if contact not in contact_list:

                    saved_client = Client.objects().get(id=data.client_id.id)

                    the_contact = CompagniUser()
                    the_contact.user_id = contact

                    saved_client.contact.append(the_contact)
                    saved_client.save()

        data = data.save()

        if not opportunite_id:

            suivie = Suivie()

            suivie.etape = global_etape[0]

            suivie.opportunite_id = data

            first_activite = Activite.objects(Q(sigle='faire_devis')).get()
            suivie.activite = first_activite.name
            suivie.sigle_activite = 'faire_devis'

            time_zones = pytz.timezone('Africa/Douala')
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")
            current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

            suivie.dateNext = current_date + datetime.timedelta(days=first_activite.jour)

            suivie.resume = first_activite.name
            suivie.description = first_activite.description

            suivie.status = False
            suivie = suivie.save()

            opp = Opportunite.objects.get(id=data.id)
            opp.suivie.append(suivie)
            opp.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('opportunite.edit', relance=request.args.get('relance')))
        else:
            return redirect(url_for('opportunite.view', opportunite_id=data.id, relance=request.args.get('relance')))

    return render_template('opportunite/edit.html', **locals())


@prefix_opportunite.route('/change/<etape_id>/<objectid:opportunite_id>')
@login_required
def change_etape(etape_id, opportunite_id):

    current_opportunite = Opportunite.objects.get(id=opportunite_id)

    if not current_user.has_roles([('super_admin', 'opportunite')], ['edit']) and current_opportunite.vendeur_id.id != current_user.id:
        flash('Vous n\'avez pas les droits necessaires pour effectuer cette action', 'warning')
        return redirect(url_for('opportunite.view', opportunite_id=opportunite_id))

    if ckeck_etape(opportunite=current_opportunite, etape=etape_id):
        flash('Etape change avec succes', 'success')
    else:
        flash('Impossible d\'appliquer ce changement d\'etat manuellement', 'danger')
    return redirect(url_for('opportunite.view', opportunite_id=opportunite_id))


@prefix_opportunite.route('/activite/<objectid:opportunite_id>')
@login_required
def relance(opportunite_id):

    title_page = 'Activite suivante'

    single = True

    current = Opportunite.objects.get(id=opportunite_id)

    datas = current.suivie
    datas.sort(reverse=True)

    return render_template('relance/index.html', **locals())


@prefix_opportunite.route('/activite/edit/<objectid:opportunite_id>', methods=['GET', 'POST'])
@prefix_opportunite.route('/activite/edit/', methods=['GET', 'POST'])
@login_required
def relance_edit(opportunite_id):

    opportunite = Opportunite.objects.get(id=opportunite_id)

    current = Suivie.objects(Q(opportunite_id=opportunite.id) & Q(status=False)).first()

    if current:
        form = FormRelance(obj=current)
        form.activite_id.data = str(current.activite)
    else:
        current = Suivie()
        form = FormRelance()

    all = Activite.objects()
    form.activite_id.choices = [('', ' ')]
    for choice in all:
        form.activite_id.choices.append((str(choice.name), choice.name))

    success = False
    if form.validate_on_submit():

        current.description = form.description.data
        current.resume = form.resume.data

        current.activite = form.activite_id.data

        current.etape = opportunite.etape
        current.dateNext = datetime.datetime.combine(function.date_convert(form.dateNext.data), datetime.datetime.min.time())

        current.status = True
        if request.args.get('planning'):
            current.status = False

        current.opportunite_id = opportunite

        current = current.save()

        if not current:
            opportunite.suivie.append(current)
            opportunite.save()

        if request.args.get('schedule'):
            current = Suivie()
            form = FormRelance()
            return render_template('relance/edit_schedule.html', **locals())
        else:
            success = True

    return render_template('relance/edit.html', **locals())


@prefix_opportunite.route('/devis/<objectid:opportunite_id>')
@login_required
def devis(opportunite_id):

    title_page = 'Devis'

    current = Opportunite.objects.get(id=opportunite_id)

    current_ref = Config_reference.objects().first()
    datas = Document.objects(Q(opportunite_id=current) & Q(devisDoc=True))

    return render_template('devis/index.html', **locals())


@prefix_opportunite.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'opportunite')], ['delete'])
def deleted():

    from ..opportunite.models_opportunite import Suivie
    from ..document.models_doc import Document

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Opportunite.objects().get(id=item)
        doc = Document.objects(opportunite_id=item_found)

        if doc:
            info['statut'] = 'NOK'
            info['message'] = 'L\'opportunite "'+item_found.name+'" est utilise par '+str(doc.count())+' autre(s) documents(s)'

        exit_suivie = Suivie.objects(opportunite_id=item_found)
        if exit_suivie:
            info['statut'] = 'NOK'
            info['message'] = 'L\'opportunite "'+item_found.name+'" est utilise par '+str(exit_suivie.count())+' autre(s) suivie(s)'

        if not doc and not exit_suivie:
            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete supprime avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data







