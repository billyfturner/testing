import dash_html_components as html
from dashboardapp.plotlydashapp.pages.page_portal import PortalLayout
from .content import ContentFactory


class Layout(PortalLayout):
    def __init__(self, app, attributes):
        super().__init__(app, attributes)
        self.content_factory = ContentFactory(app, self.page_module_name, attributes)
        self.content_factory.make()
        self.content_centre = self.content_factory.page_content
        self.marshall()






