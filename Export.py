class Export:
    """Export to file class"""
    def __init__(self,data):
        self.data=data


    def write2XML(self,filename):
        f = open(filename,"w+")
        f.write("<xml>")
        for recipe,value in self.data.iteritems():
           f.write("""<recipe>
           <name>%s</name>
           <url>%s</url>
           <intro>%s</intro>
           <instruction>%s</instruction>
           <prefecture>%s</prefecture>
           <region>%s</region>"""%(recipe,value[2],"","",value[1],value[0]))
           for ingredient,val in value[3].iteritems():
               if len(val)==2:
                   amount=val[0]
               else:
                   amount=0
                   
               f.write("""<ingredient>
               <name>%s</name>
               <unit>%s</unit>
               <amount>%f</amount>
               </ingredient>"""%(ingredient,val[1],amount))
               
           
        
           f.write("</recipe>")
        f.write("</xml>")   
        f.close()

        
    def write2JSON():
        
        
        for recipe,value in self.data.iteritems():
            jsonOb={"name":recipe,
                    "url":value[2],
                    "intro":"",
                    "instruction":"",
                    "prefecture":value[1],
                    "region":value[0]}
            for ingredient,val in value[3].iteritems():
                if len(val)==2:
                    amount=val[0]
                else:
                    amount=0
                   
                jsonIn={"ingredient":
                            {"name":ingredient,
                             "unit":val[1],
                             "amount":amount}}
                
           with open(filename, "w") as outfile:
               json.dump(jsonOb, outfile, indent=4)
               
        
            
