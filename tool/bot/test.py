# Import required libraries
from openpyxl import load_workbook
from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
from modules.sharePoint_api import API
obj=API()
obj.authenticate()
# Load Excel workbook and select subsheet
workbook = load_workbook(filename='Outreaching MS Patners.xlsx', read_only=True)
worksheet = workbook['SalesNavigator']

sp_list = obj.site.List('Leads')
sp_list.RemoveAllItems()
