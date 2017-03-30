__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import NumberInput
from models_site import Support, Horaire, Localisation, Ecran, Site, Package, Secteur


def unique_code_validator_support(form, field):
    code_unique = Support.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Support.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormSupport(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du format de contenu:', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_support])


def unique_code_validator_secteur(form, field):
    code_unique = Secteur.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Secteur.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormSecteur(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du secteur d\'activite :', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_secteur])


def unique_code_validator_tranche(form, field):
    code_unique = Horaire.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Horaire.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormTranche(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Libelle de la tranche:', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_tranche])


def unique_code_validator_local(form, field):
    code_unique = Localisation.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Localisation.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


def check_quartier(form, field):
    if form.quartier.data and not field.data:
        raise wtf.ValidationError('Selection obligatoire')


class FormLocal(wtf.Form):
    id = wtf.HiddenField()
    quartier = wtf.HiddenField()
    name = wtf.StringField(label='Nom du lieu:', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_local])
    parent = wtf.SelectField(label='Selectionner la ville :', coerce=str, validators=[check_quartier])


def unique_code_validator_ecran(form, field):
    code_unique = Ecran.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Ecran.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormEcran(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du type:', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_local])
    # multi_choice = wtf.BooleanField(label='Choix multiple d\'ecran a l\'achat :')
    outdoor = wtf.BooleanField(label='C\'est un outdoor ?:')
    cout_passage = wtf.FloatField(label='Cout du passage :', widget=NumberInput(), validators=[validators.Required('Champ obligatoire')])


def unique_code_validator_site(form, field):
    code_unique = Site.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Site.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormSite(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du site :', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_site])
    type = wtf.StringField(label='Type d\'affichage :', validators=[validators.Required(message='Champ obligatoire')])
    ecrant = wtf.SelectField(label='Selectionner un type d\'ecran :', coerce=str, validators=[validators.Required('Champ obligatoire')])
    local = wtf.SelectField(label='Selectionner un quartier :', coerce=str, validators=[validators.Required('Champ obligatoire')])
    secteur = wtf.SelectField(label='Selectionner un secteur d\'activite :', coerce=str, validators=[validators.Required('Champ obligatoire')])
    longitude = wtf.StringField(label='Longitude :')
    latitude = wtf.StringField(label='Latitude :')
    image = wtf.StringField(label='Image du site :')


def unique_code_validator_package(form, field):
    code_unique = Package.objects(
        name=field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Package.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormPackage(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom package:', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_package])
    prix_outdoor = wtf.FloatField(label='Cout du passage outdoor :', widget=NumberInput(), default='0')
    prix_indoor = wtf.FloatField(label='Cout du passage indoor:', widget=NumberInput(), default='0')
    passage = wtf.FloatField(label='Nombre de passage :', widget=NumberInput(), validators=[validators.Required('Champ obligatoire')])