'''
   GURPSLiveSheet Code Scratch
   lead developer: cblouin [at] dalhousie[:3] + '.' + canada[:2]
   
   This project is licensed under the GPLv3.0 ( http://www.gnu.org/copyleft/gpl.html )
   
   Database structure
   
   user
   campaign
   sheet
   identification_card

   sheet_cp
   
   meta_trait
   meta_skill
   
'''
# import
from pymongo import MongoClient
from bson.objectid import ObjectId

# Global scope client
# URI = 'localhost'
URI = 'mongodb://farathu.research.cs.dal.ca:27017'
client = MongoClient(host=URI, port=27017)

class mongoAPI:
    # Default connection to make it standalone
    URI = 'mongodb://farathu.research.cs.dal.ca:27017'
    client = MongoClient(host=URI, port=27017)    
    
    def __init__(self, collection_name='test'):
        # Store collection name
        self.collection_name = collection_name
        
    def _c(self):
        return mongoAPI.client['gls'][self.collection_name]
    
    def _db(self):
        return mongoAPI.client['gls']
    
    ## Read 
    def Fetch(self, name):
        # Get data from client
        x = self._c().find_one({'name':name})
        if x:
            self.data = x
            self.data['_id'] = self.data['_id']
            
    def ListNames(self):
        out = []
        for i in self._c().find():
            out.append(i['name'])
        return out
        
    ## Getter
    def Get(self, name):
        if name in self.data:
            return self.data[name]
        return None
    
    ## Setter
    def Set(self, name, vals):
        self.data[name] = vals
        
    def AppendTo(self, name, vals):
        try:
            self.data[name].append(vals)
        except:
            pass
    
    ## Write
    def Save(self):
        # Case 1 -- doesn't have an _id
        if not '_id' in self.data:
            out = self._c().insert_one(self.data) 
            self.data['_id'] = out.inserted_id
        # Case 2 -- an update operation
        else:
            _id = self.data['_id']
            del self.data['_id']
            self._c().update({'_id':_id},{'$set': self.data})
            self.data['_id'] = _id

class meta_skill(mongoAPI):
    dmods = {'E':0, 'A':-1, 'H':-2, 'VH':-3}
    def __init__(self, name=''):
        # Parent
        mongoAPI.__init__(self,'meta_skills')
        
        # attributes
        self.data = {'name':'',
                     'base':'IQ',
                     'difficulty':'E',
                     'default':-5,
                     'alt default': []}
        
        if name:
            self.Fetch(name)
            
    def Populate(self, name, base, difficulty, default):
        self.data['name'] = name
        self.data['base'] = base
        self.data['difficulty'] = difficulty
        self.data['default'] = default
        
        self.Save()
    
    def RelativeLevel(self, cp):
        # Compute the level from a cp allocation
        # By default...
        if cp == 0:
            return self.data['default']
    
        # Calculate levels
        out = meta_skill.dmods[self.data['difficulty']]
        if cp == 1:
            return out
        elif cp == 2:
            return out+1
        else:
            return out + cp / 4
            
            
        



class meta_attribute(mongoAPI):
    
    def __init__(self, name= ''):
        # Parents
        mongoAPI.__init__(self, 'meta_attributes')
        
        # Data
        self.data = {'name':'',
                     'base':10,
                     'cost':10}
        
        if name:
            self.Fetch(name)
            
    def RelativeLevel(self, cp):
        return abs(cp) / self.data['cost'] * (self.data['cost']/abs(self.data['cost']))
    
class gls_campaign(mongoAPI):
    
    def __init__(self, name = ''):
        # Parent
        mongoAPI.__init__(self, 'campaign')
        
        # Data
        self.data = {'name':name,
                     'GM': 'root@dal.ca',
                     'pwd': 'xxx123'}
        if name:
            self.Fetch(name)
            
    def SpawnSheet(self):
        out = gls_sheet(self.data['_id'])
        out.Save()
        return out
            
        
class gls_sheet(mongoAPI):
    
    def __init__(self, campaign_id, sheet_id=None):
        # Parent
        mongoAPI.__init__(self, 'sheets')
        
        # Data
        self.data = {'name':'',
                     'race':'human',
                     'ethnicity':'',
                     'age': 0,
                     'SM' : 0,
                     'height': '',
                     'weight': '',
                     'gender': '',
                     'user': 'root@dal.ca',
                     'pwd' : 'xxx123',
                     'campaign_id':campaign_id}
        
        # Create or populate
        if sheet_id != None:
            # New sheet
            x = self._c().find_one( {'_id': ObjectId(sheet_id), 'campaign_id': ObjectId(campaign_id)} )
            if x:
                self.data = x
                self.data['_id'] = str( self.data['_id'] )

        
if __name__ == "__main__":
    # DB client
    #client = GetMongoClient('localhost')
    
    x = gls_campaign('debug')
    y = x.SpawnSheet()
    print y

        
        