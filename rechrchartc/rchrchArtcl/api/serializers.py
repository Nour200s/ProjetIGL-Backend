# in it file we change the model to the python natif so that we can ofter make it in format json
from rest_framework.serializers import ModelSerializer 
from ..models import User
# import form models your model 
class UserSerializer(ModelSerializer):
    class Meta(object):
        # we put out model to serialize the model
        model = User
        fields = ['id','name','password']
        


            
