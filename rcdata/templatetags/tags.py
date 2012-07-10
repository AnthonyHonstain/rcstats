from django import template

register = template.Library()

@register.tag
def active(parser, token):
    import re
    args = token.split_contents()
    template_tag = args[0]
    if len(args) < 3:
        raise template.TemplateSyntaxError, "%r tag requires at least one argument" % template_tag
    '''
    Example args
            [u'active', u'request', u'index']
        Another call
            [u'active', u'request', u'myresults']            
        Another call            
            [u'active', u'request', u'faq']    
    '''    
    return NavSelectedNode(args[2])

class NavSelectedNode(template.Node):
    def __init__(self, url):
        self.url = url
    def render(self, context):
        '''
        Note - I found this method and the context it is called in to be
            rather confusing. I have recorded the print line debuggering here
            to help in the future.
            You can see that the NavSelectedNode is created multiple times
            for each navgiation panel.
            
        Example values (printline debugging):
            print "path:", path
            print "self.patterns: ", self.url
        
            [Tue Jul 10 16:28:07 2012] [error] path: /myresults/
            [Tue Jul 10 16:28:07 2012] [error] self.patterns:  index
            [Tue Jul 10 16:28:07 2012] [error] path: /myresults/
            [Tue Jul 10 16:28:07 2012] [error] self.patterns:  myresults
            [Tue Jul 10 16:28:07 2012] [error] path: /myresults/
            [Tue Jul 10 16:28:07 2012] [error] self.patterns:  trackdata
            [Tue Jul 10 16:28:07 2012] [error] path: /myresults/
            [Tue Jul 10 16:28:07 2012] [error] self.patterns:  ranking
            [Tue Jul 10 16:28:07 2012] [error] path: /myresults/
            [Tue Jul 10 16:28:07 2012] [error] self.patterns:  faq        
        '''        
        path = context['request'].path
        pValue = template.Variable(self.url).resolve(context)
        if (pValue == '/' or pValue == '') and not (path  == '/' or path == ''):
            return ""
        if path.startswith(pValue):
            return 'current_page_item'
        return ""