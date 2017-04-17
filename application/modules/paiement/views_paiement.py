
from ...modules import *
from models_paiement import Moyen_paiement
from form_paiement import FormMoyenPaiement

prefix = Blueprint('moyen_paiement', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'moyen_paiement')])
def index():

    title_page = 'Moyen de paiement'

    datas = Moyen_paiement.objects()

    return render_template('paiement/index.html', **locals())


@prefix.route('/view/<objectid:moyen_paiement_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'moyen_paiement')], ['edit'])
def view(moyen_paiement_id):

    title_page = 'Moyen de paiement'

    data = Moyen_paiement.objects.get(id=moyen_paiement_id)
    form = FormMoyenPaiement(obj=data)
    form.id.data = moyen_paiement_id

    return render_template('paiement/view.html', **locals())


@prefix.route('/edit/<objectid:moyen_paiement_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'moyen_paiement')], ['edit'])
def edit(moyen_paiement_id=None):

    title_page = 'Moyen de paiement'

    if moyen_paiement_id:
        data = Moyen_paiement.objects.get(id=moyen_paiement_id)
        form = FormMoyenPaiement(obj=data)
        form.id.data = moyen_paiement_id

    else:
        data = Moyen_paiement()
        form = FormMoyenPaiement()

    error_image = False
    if request.method == 'POST':

        file = request.files['file']

        if file:

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                link_save_file = '/static/uploads/'+filename
                form.logo.data = link_save_file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                error_image = True
                flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg', 'warning')

    if form.validate_on_submit() and not error_image:

        data.name = form.name.data
        data.sigle = form.sigle.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('moyen_paiement.edit'))
        else:
            return redirect(url_for('moyen_paiement.view', moyen_paiement_id=data.id))

    return render_template('paiement/edit.html', **locals())