# coding=utf-8
from ...modules import *


class ExcelParser(object):

    def read_excel(self, excel_name):
        wb = xlrd.open_workbook(excel_name)
        items = []
        # sheet = wb.sheet_by_name('Sheet1')
        for sheet in wb.sheets():
            number_of_rows = sheet.nrows
            number_of_columns = sheet.ncols

            headers = [cell.value for cell in sheet.row(0)]

            response = self.check_header(headers)

            if response:
                rows = []
                for row in range(1, number_of_rows):
                    values = []
                    for col in range(number_of_columns):
                        value = (sheet.cell(row,col).value)
                        try:
                            value = str(int(value))
                        except ValueError:
                            pass
                        finally:
                            values.append(value)
                    item = Arm(*values)
                    items.append(item.__dict__)

        return items

    def check_header(self, header_list):

        response = True

        if header_list[0].lower() != 'nom':
            response = False

        if header_list[1].lower() != 'categorie':
            response = False

        if header_list[2].lower() != 'region':
            response = False

        if header_list[3].lower() != 'ville':
            response = False

        if header_list[4].lower() != 'quartier':
            response = False

        if header_list[5].lower() != 'rue':
            response = False

        if header_list[6].lower() != 'bp':
            response = False

        if header_list[7].lower() != 'reperage':
            response = False

        if header_list[8].lower() != 'email':
            response = False

        if header_list[9].lower() != 'phone':
            response = False

        if header_list[10].lower() != 'website':
            response = False

        if header_list[11].lower() != 'facebook':
            response = False

        if header_list[12].lower() != 'description':
            response = False

        if header_list[13].lower() != 'logo':
            response = False

        if header_list[14].lower() != 'image':
            response = False

        if header_list[15].lower() != 'dossier':
            response = False

        if header_list[16].lower() != 'latitude':
            response = False

        if header_list[17].lower() != 'longitude':
            response = False

        return response


class Arm(object):
    def __init__(self, nom, categorie, region, ville, quartier, rue, bp, reperage, email, phone, website, facebook, description, logo, image, dossier, latitude, longitude):
        self.nom = nom
        self.categorie = categorie
        self.region = region
        self.ville = ville
        self.quartier = quartier
        self.rue = rue
        self.bp = bp
        self.reperage = reperage
        self.email = email
        self.phone = phone
        self.website = website
        self.facebook = facebook
        self.description = description
        self.logo = logo
        self.image = image
        self.dossier = dossier
        self.latitude = latitude
        self.longitude = longitude

    # def __str__(self):
    #     return("Arm object:\n"
    #            "  Arm_id = {0}\n"
    #            "  DSPName = {1}\n"
    #            "  DSPCode = {2}\n"
    #            "  HubCode = {3}\n"
    #            "  PinCode = {4} \n"
    #            .format(self.id, self.title, self.body,
    #                    self.pub_date, self.category))