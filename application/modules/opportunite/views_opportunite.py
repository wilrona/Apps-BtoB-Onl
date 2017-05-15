__author__ = 'User'


from form_opportunite import FormOpportunite, FormRelance
from models_opportunite import Opportunite, Etape, Suivie, Activite, Libelle_Opportunite
from ..compagnie.forms_compagnie import FormClient
from ..company.models_company import Config_reference
from ..document.models_doc import Document
from ..compagnie.models_compagnie import Compagnie, Categorie
from ..user.models_user import Users
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

    customer = Compagnie.objects.get(id=data.client_id.id)
    form_client = FormClient(obj=customer)


    form_client.idcategorie.data = [str(cat.id) for cat in customer.idcategorie]
    if customer.maincategorie:
        form_client.maincategorie.data = str(customer.maincategorie.id)

    contact = Users.objects.get(id=data.contact_id.id)
    form_contact = FormUser(obj=contact)

    form.vendeur_id.data = str(data.vendeur_id.id)

    form_client.id.data = str(customer.id)
    form.id.data = str(opportunite_id)

    devis_count = Document.objects(Q(opportunite_id=data) & Q(devisDoc=True)).count()

    from ..user.models_user import Roles
    admin_role = Roles.objects(valeur='super_admin').first()

    if current_user.has_roles(['super_admin']):
        all_vendeur = Users.objects(Q(user__gt=0) & Q(activated=True))
    else:
        all_vendeur = Users.objects(Q(user__gt=0) & Q(activated=True) & Q(roles__role_id__ne=admin_role))

    form.vendeur_id.choices = [('', ' ')]
    for choice in all_vendeur:
        form.vendeur_id.choices.append((str(choice.id), choice.first_name+' '+choice.last_name))

    etape_list = Etape.objects(actif=True).order_by('order')

    last_etape = Etape.objects(actif=True).order_by('-order').first()

    client_list = Compagnie.objects(activated=True)

    devis_count = Document.objects(Q(opportunite_id=data) & Q(devisDoc=True)).count()

    return render_template('opportunite/view.html', **locals())


@prefix_opportunite.route('/edit/<objectid:opportunite_id>', methods=['GET', 'POST'])
@prefix_opportunite.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit(opportunite_id=None):

    title_page = 'Opportunites'

    if opportunite_id:
        data = Opportunite.objects.get(id=opportunite_id)

        if data.etape == global_etape[3]:
            return redirect(url_for('opportunite.view', opportunite_id=opportunite_id))

        if not current_user.has_roles([('super_admin', 'opportunite')], ['edit']) and data.vendeur_id.id != current_user.id:
            return redirect(url_for('opportunite.view', opportunite_id=opportunite_id))

        form = FormOpportunite(obj=data)

        customer = Compagnie.objects.get(id=data.client_id.id)
        form_client = FormClient(prefix="client", obj=customer)

        form_client.idcategorie.data = [str(cat.id) for cat in customer.idcategorie]
        form_client.maincategorie.data = str(customer.maincategorie.id)

        if request.method == 'GET':
            form_client.maincategorie.choices = [('', 'Faite le choi de la categorie principale')]
            for choice in customer.idcategorie:
                form_client.maincategorie.choices.append((str(choice.id), choice.name))

        contact = Users.objects.get(id=data.contact_id.id)
        form_contact = FormUser(obj=contact)

        form.vendeur_id.data = str(data.vendeur_id.id)

        form_client.id.data = str(customer.id)
        form.id.data = str(opportunite_id)

        devis_count = Document.objects(Q(opportunite_id=data) & Q(devisDoc=True)).count()

        flash('Vous ne pouvez plus modifier les informations du client et de contact du client. ', 'warning')
    else:
        data = Opportunite()
        form = FormOpportunite()

        customer = Compagnie()
        form_client = FormClient(prefix="client")

        contact = Users()
        form_contact = FormUser()

        if request.method == 'GET':
            form.vendeur_id.data = str(current_user.id)

        if 'client_exist' in request.form and request.form['client_exist']:
            form_client.id.data = request.form['client_exist']

        if 'contact_exist' in request.form and request.form['contact_exist']:
            form_contact.id.data = request.form['contact_exist']

    form_client.notCat.data = '1'

    from ..user.models_user import Roles
    admin_role = Roles.objects(valeur='super_admin').first()

    if current_user.has_roles(['super_admin']):
        all_vendeur = Users.objects(Q(user__gt=0) & Q(activated=True))
    else:
        all_vendeur = Users.objects(Q(user__gt=0) & Q(activated=True) & Q(roles__role_id__ne=admin_role))

    form.vendeur_id.choices = [('', ' ')]
    for choice in all_vendeur:
        form.vendeur_id.choices.append((str(choice.id), choice.first_name+' '+choice.last_name))

    form_client.idcategorie.data = ''
    form_client.idcategorie.choices = [('', '')]
    form_client.maincategorie.data = ''
    form_client.maincategorie.choices = [('', 'Faite le choix de la categorie principale')]

    etape_list = Etape.objects(actif=True).order_by('order')
    client_list = Compagnie.objects()

    libelle = []
    if not opportunite_id:
        libelle = Libelle_Opportunite.objects(actif=True)

    current_client = None
    if request.method == 'POST' and 'client_exist' in request.form and request.form['client_exist']:

        current_client = Compagnie.objects.get(id=request.form['client_exist'])

        form_client.name.data = current_client.name
        form_client.email.data = current_client.email
        form_client.raison.data = current_client.raison
        form_client.phone.data = current_client.phone
        form_client.ville.data = current_client.ville
        form_client.quartier.data = current_client.quartier

    current_contact = None
    if request.method == 'POST' and 'contact_exist' in request.form and request.form['contact_exist']:

        current_contact = Users.objects.get(id=request.form['contact_exist'])

        form_contact.id.data = current_contact.id
        form_contact.email.data = current_contact.email
        form_contact.first_name.data = current_contact.first_name
        form_contact.last_name.data = current_contact.last_name
        form_contact.fonction.data = current_contact.fonction
        form_contact.phone.data = current_contact.phone

    if form.validate_on_submit() and form_client.validate_on_submit() and form_contact.validate_on_submit():

        if not opportunite_id:
            data.name = form.name.data

        if data.vendeur_id and data.vendeur_id.id != current_user.id:
            vendeur = Users.objects.get(id=form.vendeur_id.data)
            data.vendeur_id = vendeur
        else:
            vendeur = Users.objects.get(id=current_user.id)
            data.vendeur_id = vendeur

        data.note = form.note.data

        if 'client_exist' in request.form and request.form['client_exist']:
            data.client_id = current_client
        else:
            if not opportunite_id:
                customer.raison = form_client.raison.data
                customer.name = form_client.name.data
                customer.ville = form_client.ville.data
                customer.quartier = form_client.quartier.data

                customer.email = form_client.email.data
                customer.phone = form_client.phone.data
                customer.activated = False
                customer.verify = False
                customer.source = "opportunite"

                customer = customer.save()

                data.client_id = customer

        if 'contact_exist' in request.form and request.form['contact_exist']:
            data.contact_id = current_contact
            data.etape = global_etape[0]
        else:
            if not opportunite_id:

                contact.email = form_contact.email.data
                contact.first_name = form_contact.first_name.data
                contact.last_name = form_contact.last_name.data
                if form_contact.fonction.data:
                    contact.fonction = form_contact.fonction.data
                contact.phone = form_contact.phone.data
                contact.activated = False
                contact.source = "opportunite"
                contact.user = 0
                contact = contact.save()

                data.contact_id = contact
                data.etape = global_etape[0]

                # Sauvegarde du contact dans l'entreprise en cours.
                contact_compagnie = data.client_id.idcontact
                user_compagnie = data.client_id.iduser
                if contact not in contact_compagnie and contact not in user_compagnie:
                    cli = Compagnie.objects.get(id=data.client_id.id)
                    cli.idcontact.append(contact)
                    cli.save()

        data = data.save()

        if not opportunite_id:

            suivie = Suivie()

            suivie.etape = global_etape[0]

            suivie.opportunite_id = data

            first_activite = Activite.objects(Q(sigle='faire_devis')).get()
            suivie.activite = first_activite.name
            suivie.sigle_activite = 'faire_devis'

            time_zones = tzlocal()
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
        if request.args.get('schedule'):
            current.status = False

        current.opportunite_id = opportunite

        current = current.save()

        if current not in opportunite.suivie:
            opportunite.suivie.append(current)
            opportunite.save()

        if request.args.get('schedule'):
            current = Suivie()
            form = FormRelance()

            form.description.data = ""
            form.resume.data = ""
            form.activite_id.data = ""
            form.dateNext.data = ""

            all = Activite.objects()
            form.activite_id.choices = [('', ' ')]
            for choice in all:
                form.activite_id.choices.append((str(choice.name), choice.name))

        else:
            success = True

    if request.args.get('schedule'):
        return render_template('relance/edit_schedule.html', **locals())
    else:
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







