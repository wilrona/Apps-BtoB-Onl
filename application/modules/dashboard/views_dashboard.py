__author__ = 'User'


from ...modules import *
from ..opportunite.models_opportunite import Opportunite, Suivie
from ..document.models_doc import Document
from ..compagnie.models_compagnie import Compagnie, Claim, Relation
from ..company.models_company import Config_reference


prefix = Blueprint('dashboard', __name__)


@prefix.route('/')
@login_required
def index():

    # time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.date.today()
    current_ref = Config_reference.objects().first()


    ## liste des opportunites qui n'appartiennent pas au client
    if not current_user.has_roles([('super_admin', 'opportunite')]):
        ids_opportunity = [opportunite.id for opportunite in Opportunite.objects(vendeur_id__ne=current_user.id)]
    else:
        ids_opportunity = []

    ## Liste des activites qui sont superieurs a la date en cours
    suivies = Suivie.objects(Q(status=False) & Q(dateNext__gt=date_auto_nows))
    next_activite = 0
    for suivie in suivies:
        next_activite += 1

    ## Liste des activites qui sont inferieurs a la date en cours
    suivies_past = Suivie.objects(Q(status=False) & Q(dateNext__lt=date_auto_nows))
    past_activite = 0
    for suivie in suivies_past:
        past_activite += 1

    # Compte le nombre de client
    count_client = Compagnie.objects(verify=True).count()

    if current_user.has_roles([('super_admin', 'devis')]):
        count_devis = Document.objects(Q(devisDoc=True) & Q(status__lt=3)).count()
        list_devis = Document.objects(Q(devisDoc=True) & Q(status__lt=2)).order_by('-createDate')
        ca_devis = Document.objects(Q(devisDoc=True) & Q(status__lt=3)).order_by('-createDate')
    else:
        count_devis = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=True) & Q(status__lt=3)).count()

        list_devis = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=True) & Q(status__lt=2)).order_by('-createDate')
        ca_devis = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=True) & Q(status__lt=3)).order_by('-createDate')

    # Compte le nombre de facture
    if current_user.has_roles([('super_admin', 'facture')]):
        count_fact = Document.objects(Q(devisDoc=False) & Q(status=2)).count()
        list_fact = Document.objects(Q(devisDoc=False) & Q(status=2))
    else:
        count_fact = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=False) & Q(status=2)).count()
        list_fact = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=False) & Q(status=2))

    # Calcul du chiffre d'affaire realise en fonction des factures payees de l'utilisateur
    CA_real = 0
    for fact in list_fact:
        CA_real += fact.montant_reglement()

    # Calcul du chiffre d'affaire previsionnel en fonction des devis de l'utilisateur
    CA_prev = 0
    for devis in ca_devis:
       CA_prev += devis.montant

    # liste des suivies du jours en cours
    # suvie_day = Suivie.objects(Q(status=False) & Q(dateNext__gte=date_auto_nows)).order_by('-dateNext')

    suvie_later = Suivie.objects(Q(status=False) & Q(dateNext__lt=date_auto_nows)).order_by('-dateNext')

    # liste des activites suivantes
    suivie_next = Suivie.objects(Q(status=False) & Q(dateNext__gte=date_auto_nows)).order_by('-dateNext')

    # liste des opportunites
    if current_user.has_roles([('super_admin', 'opportunite')]):
        list_opportunite = Opportunite.objects(etape__ne="win").order_by('-createDate')
    else:
        list_opportunite = Opportunite.objects(Q(vendeur_id=current_user.id) & Q(etape__ne="win")).order_by('-createDate')

    claim_count = 0
    if current_user.has_roles([('super_admin', 'claim')]):
        claim_count = Claim.objects(Q(statut=1) | Q(statut=0)).count()

    relation_count = 0
    if current_user.has_roles([('super_admin', 'relation')]):
        relation_count = Relation.objects(Q(statut=1) | Q(statut=0)).count()



    return render_template('dashboard/index.html', **locals())