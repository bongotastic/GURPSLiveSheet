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
            self.data['_id'] = str(self.data['_id'])        
        
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
        self._c().remove({'name': self.data['name']})
        self._c().insert_one(self.data)    

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
            
    def AddAltDefault(self, name, mod):
        self.data['alt default'].append({'name':name, 'mod':mod})
        self.Save()
        
    def Save(self):
        client.gls.meta_skills.remove({'name': self.data['name']})
        client.gls.meta_skills.insert_one(self.data)

    def GetDefaults(self):
        return self.data['alt default']
    
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
            
            
        


def GetMongoClient( URI ):
    ''' Get a Mongo Client from a particular URI
    '''
    # Get a client
    if not client:
        client = MongoClient(host=URI, port=27017)
    
    return client
    


class GLS_sheet:
    '''
       Interface for a character sheet.
    '''
    
    def __init__(self, campaign, user='GM', secret_id=''):
        '''
        '''
        # IDs
        self.campaign = campaign
        self._id = None
        
        # Owner
        self.user = user
        self.secret_id = secret_id
        
        # Query for self
        x = self.campaign.client.gls.sheet.find_one({'user':user, 'secret_id':secret_id, 'campaign_id':ObjectId(campaign.GetID())})
        if not x:
            self.SetupNewSheet()
        else:
            self.FromJSON(x)
            
    def SetupNewSheet(self):
        # Initiate the entry and recover the _id
        self._id = str(self.campaign.client.gls.sheet.insert_one({'campaign_id':ObjectId(self.campaign.GetID()), 
                                                              'user':self.user, 
                                                              'secret_id': self.secret_id}).inserted_id)
        
    
    def FromJSON(self, data):
        pass
        
        
class GLS_campaign:
    '''
    '''
    def __init__(self, client, name='debug', GM='root'):
        '''
        '''
        # Logic attributes
        self.name = name
        self.GM   = GM
        
        # Database
        self.client = client
        
        # Fetch of create entry
        x = self.client.gls.campaign.find_one({'GM':GM, 'name':name})
        if x:
            self.FromJSON(x)
        else:
            # Create the instance
            self.uid = self.client.gls.campaign.insert_one( self.AsJSON() ).inserted_id
        
    def AsJSON(self):
        '''
           Generate a JSON from an instance
        '''
        out = { 'name': self.name, 'GM': self.GM }
        
        return out
    
    def FromJSON(self, data):
        # Build instance from a JSON object
        self.name = data['name']
        self.GM   = data['GM']
        self.uid  = str(data['_id'])
        
    # Getter
    def GetID(self):
        return self.uid
    
    # Action
    def GetSheet(self, owner, secret_id):
        # Get Sheet
        sheet = GLS_sheet(self, owner, secret_id)
        return sheet
        
        
if __name__ == "__main__":
    # DB client
    #client = GetMongoClient('localhost')
    
    x = meta_skill('Administration')
    print x
    #x.Populate('Administration','IQ','A',-5)
    #x.Save()
    
    # Create a campaign
    #campaign = GLS_campaign(client)
    
    # Create a sheet
    #sheet = campaign.GetSheet('GM', 'debug1')
        
        