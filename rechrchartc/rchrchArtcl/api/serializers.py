# in it file we change the model to the python natif so that we can ofter make it in format json
from rest_framework.serializers import ModelSerializer 
from ..models import *

# import form models your model 
class UserSerializer(ModelSerializer):
    class Meta(object):
        # we put out model to serialize the model
        model = User
        fields = ['id','name','password']

class ModerateursSerializer(ModelSerializer):
    class Meta(object):
        model = Moderateurs
        fields = ['id','name','email','password']
        


# When we retreive an article we want to retreive also : its key words, references, authors and their institutions

            
class ArticleSerializer(ModelSerializer):

    class Meta:
        model = Article
        fields = ['id', 'titre','auteurs','institutions','references','mot_cles','resume','contenu','pdf','date_pub']