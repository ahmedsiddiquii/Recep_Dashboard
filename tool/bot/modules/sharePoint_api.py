from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
class API:
    def authenticate(self):
        sharepointUsername = "ahmed.siddiqui@it-service-sia.com"
        sharepointPassword = "Kos03150"
        sharepointSite = "https://itservicesialatvia.sharepoint.com/sites/IT-Service-SIA"
        website = "https://itservicesialatvia.sharepoint.com"
        authcookie = Office365(website, username=sharepointUsername,
                               password=sharepointPassword).GetCookies()
        site = Site(sharepointSite, version=Version.v365, authcookie=authcookie)
        self.site=site
        return self.site
    def read_list_data(self):
        new_list = self.site.List('Leads')
        list_items = new_list.GetListItems("empty_emails")
        all_data = new_list.GetListItems("All Items")
        return list_items,all_data
    def update_list_data(self,data,kind='Update'):
        new_list = self.site.List('Leads')
        new_list.update_list_items([data], kind=kind)
        return 






