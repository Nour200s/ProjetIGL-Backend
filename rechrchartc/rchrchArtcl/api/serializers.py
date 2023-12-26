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
        fields = ['id','name','password']
        


# When we retreive an article we want to retreive also : its key words, references, authors and their institutions
class InstitutionSerializer(ModelSerializer):
    class Meta:
        model = Institution
        fields = ['nom']

class AuteursSerializer(ModelSerializer):
    institutions = InstitutionSerializer()  # Include Institution data

    class Meta:
        model = Auteurs
        fields = ['nom', 'institutions']  
            


# Serialization of the Mot cle            
class MotCleSerializer(ModelSerializer):
    class Meta:
        model = Mot_cle
        fields = ['mot'] 

# Serialization of the references            
class ReferencesSerializer(ModelSerializer):
    class Meta:
        model = References
        fields = ['contenu'] 
            
class ArticleSerializer(ModelSerializer):
    auteurs = AuteursSerializer(many=True, read_only=True)
    mot_cle = MotCleSerializer(many=True, read_only=True)
    references=ReferencesSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'titre', 'resume', 'contenu', 'pdf', 'date_pub', 'auteurs', 'mot_cle', 'references']